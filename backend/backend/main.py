import os
from dotenv import load_dotenv

# Load .env FIRST — before any service imports that read os.getenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from functools import lru_cache
import time

from backend.services.nlp_service import extract_text_from_pdf, extract_topics, compute_overall_similarity, topic_wise_similarity_ranking, get_model, get_util
from backend.services.youtube_service import fetch_youtube_videos, get_video_summary
from backend.services.email_service import send_quiz_score_email
from backend.utils.auth_utils import get_current_user
from backend.utils.database import analyses_collection, quiz_results_collection
from backend.data.pyqs import get_pyqs_by_topic, get_all_categories
import uvicorn
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ExamBridge AI API")

# Persistent storage for Topic of the Day
current_topic_of_the_day = None

# Response cache for faster API mapping (in-memory, 10-minute TTL)
_resource_cache = {}
CACHE_TTL = 600  # 10 minutes

# Preload models at startup
@app.on_event("startup")
async def startup_event():
    """Preload NLP models to reduce first request latency"""
    from backend.services.nlp_service import preload_models
    preload_models()


# -------------------------------
# CORS CONFIG - Allow your GitHub Pages site
# -------------------------------
origins = [
    "https://pothulaannapurna8.github.io",
    "https://exam-bridge-nexus.onrender.com",
    "http://localhost:3000",
    "http://localhost:5173", # Vite dev server
    "http://localhost:5174", # Vite dev server (alternative)
    "http://localhost:5175", # Vite dev server (current)
    "http://localhost:5176", # Vite dev server (latest)
    "http://127.0.0.1:5500",
    "*" # Allowed for debugging, narrow down in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Auth Router
from backend.routes.auth import router as auth_router
app.include_router(auth_router, prefix="/auth")

PDF_FOLDER = "gate_pdfs"

@app.get("/")
def home():
    logger.info("Root endpoint hit.")
    return {"status": "ExamBridge AI API is Running 🚀"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint hit.")
    return {"status": "running"}

@app.post("/analyze/{branch}")
async def analyze(branch: str, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    """
    Main endpoint for the GitHub frontend.
    1. Authenticates user.
    2. Extracts text from uploaded PDF.
    3. Compares against the specified GATE branch PDF.
    4. Returns similarity score, gaps, and summarized YouTube lectures.
    5. Saves analysis to MongoDB.
    """
    # 0. Authenticate User
    logger.info(f"Analyzing with token: {token[:10]}...")
    user_email = get_current_user(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    logger.info(f"Received analysis request from {user_email} for branch: {branch}")
    
    # 1. Extract College Syllabus Text
    try:
        content = await file.read()
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
        
        logger.info(f"File '{file.filename}' read successfully. Size: {len(content)} bytes.")
        
        # Extract text without signal-based timeout for Windows compatibility
        college_text = extract_text_from_pdf(content)
        
        if not college_text.strip():
            logger.warning("Empty text extracted from uploaded PDF.")
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error during PDF processing: {e}")
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")

    # 2. Load GATE Syllabus Topics (Database Priority)
    gate_topics = []
    from backend.utils.database import gate_topics_collection
    
    # Try fetching from database first
    if gate_topics_collection is not None:
        try:
            db_topics_entry = gate_topics_collection.find_one({"branch": branch})
            if db_topics_entry:
                gate_topics = db_topics_entry.get("topics", [])
                logger.info(f"Loaded {len(gate_topics)} predefined GATE topics for '{branch}' from MongoDB.")
        except Exception as e:
            logger.warning(f"Failed to fetch GATE topics from DB: {e}. Falling back to PDF.")

    if not gate_topics:
        # Fallback to PDF extraction
        gate_pdf_path = os.path.join(PDF_FOLDER, f"{branch}.pdf")
        if not os.path.exists(gate_pdf_path):
            gate_pdf_path = f"{branch}.pdf" # check root
            
        if not os.path.exists(gate_pdf_path):
            logger.error(f"GATE branch file not found: {gate_pdf_path}")
            raise HTTPException(status_code=404, detail=f"GATE branch {branch} not found and no DB record exists.")
            
        try:
            with open(gate_pdf_path, "rb") as f:
                gate_content = f.read()
                gate_text = extract_text_from_pdf(gate_content)
                gate_topics = extract_topics(gate_text)
                logger.info(f"GATE syllabus for '{branch}' extracted from PDF (fallback).")
        except Exception as e:
            logger.error(f"Error reading GATE syllabus PDF: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process GATE syllabus: {str(e)}")

    # 3. Perform AI Analysis
    logger.info("Starting AI NLP analysis...")
    try:
        # For overall similarity, we still use the full text if available, 
        # but for matching we use the extracted topics.
        # Fallback for gate_text if we only have topics from DB
        gate_text_for_sim = " ".join(gate_topics) 
        
        overall_similarity = compute_overall_similarity(college_text, gate_text_for_sim)
        college_topics = extract_topics(college_text)
        results = topic_wise_similarity_ranking(college_topics, gate_topics)
    except Exception as e:
        logger.error(f"AI Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # 4. Get Enriched Recommendations (Gaps + Summaries)
    high_priority_gaps = []
    medium_priority_gaps = []
    
    for r in results:
        priority = r.get("priority", "")
        if "🚨 High" in priority or "High" in priority:
            high_priority_gaps.append(r)
        elif "🟡 Medium" in priority or "Medium" in priority:
            medium_priority_gaps.append(r)
    
    # Determine which gaps to use for recommendations
    if high_priority_gaps:
        priority_gaps = high_priority_gaps[:3]  # Reduce to 3 for faster processing
        gap_type = "high priority"
    elif medium_priority_gaps:
        priority_gaps = medium_priority_gaps[:3]  # Reduce to 3 for faster processing
        gap_type = "medium priority"
    else:
        # No priority gaps found - create recommendations for top topics anyway
        logger.info("No priority gaps found. Creating recommendations for top GATE topics...")
        priority_gaps = results[:3]  # Reduce to 3 for faster processing
        gap_type = "recommended"
        for r in priority_gaps:
            r["priority"] = "📚 Recommended"  # Override priority for display
    
    recommendations = []
    youtube_links = []
    
    logger.info(f"Found {len(priority_gaps)} {gap_type} gaps. Fetching recommendations...")
    
    try:
        model = get_model()
        util = get_util()
    except Exception as e:
        logger.error(f"Failed to load NLP model for summarization: {e}")
        # Continue without model - just provide videos without summaries
        model = None
        util = None

    # Simplified sequential processing for debugging
    for i, gap in enumerate(priority_gaps):
        topic_name = gap["gate_topic"]
        
        # Clear cache for every second topic to ensure variety
        if i % 2 == 0:
            from backend.services.youtube_service import clear_video_cache
            clear_video_cache()
        
        try:
            videos = fetch_youtube_videos(topic_name)
            
            if videos and len(videos) > 0 and isinstance(videos[0], dict) and "error" not in videos[0]:
                top_video = videos[0]
                youtube_links.append(top_video['url'])
                
                # Only generate summary if model is available
                if model and util:
                    try:
                        v_id = top_video['url'].split("v=")[-1]
                        summary = get_video_summary(v_id, topic_name, model, util)
                        top_video['summary'] = summary
                    except Exception as e:
                        logger.warning(f"Summary generation failed for {topic_name}: {e}")
                        top_video['summary'] = "Summary not available."
                else:
                    top_video['summary'] = "Summary temporarily disabled."
                
                recommendations.append({
                    "topic": topic_name,
                    "video": top_video
                })
            else:
                logger.warning(f"No videos found for {topic_name}")
                
        except Exception as e:
            logger.error(f"Error processing topic {topic_name}: {e}")
            continue

    comparison_summary = f"Your syllabus has an overall match of {round(overall_similarity, 1)}% with the GATE {branch} syllabus. We identified {len(high_priority_gaps)} critical gaps where topics are either missing or have low similarity."

    logger.info("Generating Topic of the Day...")
    topic_of_the_day = None
    global current_topic_of_the_day
    if results:
        # Pick highest priority topic not mastered
        highest_priority_gap = next((r for r in results if "High" in r.get("priority", "")), None)
        if not highest_priority_gap:
            highest_priority_gap = next((r for r in results if "Medium" in r.get("priority", "")), None)
        if not highest_priority_gap:
            highest_priority_gap = results[0]
            
        selected_topic_name = highest_priority_gap["gate_topic"]
        
        # Explain
        priority_label = highest_priority_gap.get("priority", "Low").replace("🚨 ", "").replace("🟡 ", "").replace("✅ ", "")
        explanation = f"This topic is selected today because it is a {priority_label}-priority concept with significant weightage in GATE Operating Systems. It is a critical link in your syllabus coverage."
        
        # Store persistently in memory
        current_topic_of_the_day = {
            "topic_name": selected_topic_name,
            "explanation": explanation
        }
        
        topic_of_the_day = {
            "Topic Name": selected_topic_name,
            "Explanation": explanation
        }

    logger.info("Analysis complete. Returning response.")
    
    analysis_data = {
        "user_email": user_email,
        "branch": branch,
        "comparison_result": comparison_summary,
        "overall_similarity": round(overall_similarity, 1),
        "critical_gaps": len(high_priority_gaps),
        "gate_topic_count": len(gate_topics),
        "results": results,
        "recommendations": recommendations,
        "topic_of_the_day": topic_of_the_day,
        "created_at": datetime.utcnow()
    }

    try:
        analyses_collection.insert_one(analysis_data)
        logger.info(f"Analysis saved to database for user {user_email}")
    except Exception as e:
        logger.error(f"Failed to save analysis to database: {e}")

    # Return structured JSON as requested
    # Remove _id from response
    analysis_data.pop("_id", None)
    return analysis_data


@app.get("/history")
async def get_history(token: str = Depends(oauth2_scheme)):
    """
    Returns the analysis history for the authenticated user.
    Falls back to empty list if database is unavailable.
    """
    user_email = get_current_user(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    logger.info(f"Fetching history for user: {user_email}")
    
    # Check if database is available
    if analyses_collection is None:
        logger.warning("Database unavailable, returning empty history")
        return []
    
    try:
        cursor = analyses_collection.find({"user_email": user_email}).sort("created_at", -1)
        history = list(cursor)
        for item in history:
            item["_id"] = str(item["_id"])
        return history
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        # Return empty list instead of error for better UX
        return []

@app.get("/topic-of-the-day")
async def get_tod():
    """
    Returns the persistent Topic of the Day with a fresh live YouTube search.
    """
    global current_topic_of_the_day
    if not current_topic_of_the_day:
        raise HTTPException(status_code=404, detail="No syllabus has been analyzed yet to generate a Topic of the Day.")
    
    topic_name = current_topic_of_the_day["topic_name"]
    explanation = current_topic_of_the_day["explanation"]
    
    # 3. Fetch YouTube videos (Dynamic ranking every time)
    logger.info(f"Fetching fresh YouTube recommendation for TOD: {topic_name}")
    videos = fetch_youtube_videos(f"{topic_name} Operating Systems GATE", max_results=1)
    
    best_video = None
    if videos and isinstance(videos[0], dict) and "error" not in videos[0]:
        v = videos[0]
        raw_views = v.get("views", 0)
        raw_likes = v.get("likes", 0)
        # Format for human-readable display
        views_str = f"{raw_views:,}" if raw_views > 0 else "N/A"
        likes_str = f"{raw_likes:,}" if raw_likes > 0 else "N/A"
        
        # Get video ID and generate summary
        video_url = v.get("url", "#")
        video_id = video_url.split("v=")[-1] if "v=" in video_url else ""
        
        # Generate summary using AI
        summary = "Summary not available."
        try:
            model = get_model()
            util = get_util()
            if model and util and video_id:
                from backend.services.youtube_service import get_video_summary
                summary = get_video_summary(video_id, topic_name, model, util, v.get("title", ""))
        except Exception as e:
            logger.warning(f"Summary generation failed for TOD video: {e}")
        
        best_video = {
            "Title": v.get("title", "N/A"),
            "Channel": v.get("channel", "N/A"),
            "Views": views_str,
            "Likes": likes_str,
            "Link": video_url,
            "Thumbnail": v.get("thumbnail", ""),
            "Summary": summary
        }
    
    return {
        "Topic": topic_name,
        "Explanation": explanation,
        "Best Video": best_video
    }

@app.get("/resources/{topic}")
async def get_resources_for_topic(topic: str):
    """
    Returns ranked YouTube videos for a given topic using TubeMatix scoring.
    Returns top 3 videos ranked by educational relevance.
    Responses are cached for 10 minutes to optimize API performance.
    
    Args:
        topic: str, the learning topic to fetch videos for
    
    Returns:
        dict with topic and list of ranked videos with TubeMatix scores
    """
    # Check cache first
    if topic in _resource_cache:
        cached_data, timestamp = _resource_cache[topic]
        if time.time() - timestamp < CACHE_TTL:
            logger.info(f"Returning cached resources for topic: {topic}")
            return cached_data
    
    logger.info(f"Fetching TubeMatix-ranked resources for topic: {topic}")
    
    try:
        from backend.services.youtube_service import fetch_and_rank_videos_by_topic
        
        videos = fetch_and_rank_videos_by_topic(topic, max_results=10, top_n=3)
        
        # Format response
        formatted_videos = []
        for v in videos:
            formatted_videos.append({
                "id": v.get("id", ""),
                "title": v.get("title", ""),
                "channel": v.get("channel", ""),
                "url": v.get("url", ""),
                "thumbnail": v.get("thumbnail", ""),
                "duration": v.get("duration", ""),
                "views": v.get("views", 0),
                "likes": v.get("likes", 0),
                "tubematix_score": round(v.get("tubematix_score", 0), 2)
            })
        
        response_data = {
            "topic": topic,
            "videos": formatted_videos,
            "total": len(formatted_videos)
        }
        
        # Cache the response
        _resource_cache[topic] = (response_data, time.time())
        logger.info(f"Cached and returning {len(formatted_videos)} ranked videos for '{topic}'")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching resources for topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch resources: {str(e)}")

# ─── PYQ (Previous Year Questions) Endpoints ───
@app.get("/pyqs/categories")
def pyq_categories():
    """Return all available PYQ categories."""
    return {"categories": get_all_categories()}

@app.get("/pyqs/{topic}")
def pyq_by_topic(topic: str):
    """Return PYQs matching or related to the given topic."""
    results = get_pyqs_by_topic(topic)
    return {"topic": topic, "results": results}

from backend.utils.database import quiz_results_collection
from pydantic import BaseModel

class QuizResult(BaseModel):
    topic: str
    score: int
    total: int
    percentage: float

@app.post("/quiz_results")
def submit_quiz_result(result: QuizResult, token: str = Depends(oauth2_scheme)):
    """Save user quiz result. Returns success even if database is unavailable."""
    user_email = get_current_user(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if database is available
    if quiz_results_collection is None:
        logger.warning("Database unavailable, quiz result will not be persisted")
        # Return success anyway so frontend doesn't show error
        return {"msg": "Quiz result received (not persisted - database unavailable)"}
    
    try:
        doc = result.dict()
        doc["user_email"] = user_email
        doc["created_at"] = datetime.utcnow()
        quiz_results_collection.insert_one(doc)
        return {"msg": "Quiz result saved successfully"}
    except Exception as e:
        logger.error(f"Failed to save quiz result: {e}")
        # Return success anyway so frontend doesn't show error
        return {"msg": "Quiz result received (save failed)"}

@app.get("/quiz_history")
def get_quiz_history(token: str = Depends(oauth2_scheme)):
    """Get all quiz results for the user. Falls back to empty list if database unavailable."""
    user_email = get_current_user(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if database is available
    if quiz_results_collection is None:
        logger.warning("Database unavailable, returning empty quiz history")
        return []
    
    try:
        results = list(quiz_results_collection.find({"user_email": user_email}).sort("created_at", -1))
        for r in results:
            r["_id"] = str(r["_id"])
        return results
    except Exception as e:
        logger.error(f"Failed to fetch quiz history: {e}")
        # Return empty list instead of error for better UX
        return []


@app.post("/send_quiz_score_email")
def send_quiz_score_email_endpoint(token: str = Depends(oauth2_scheme)):
    """
    Send quiz score summary email to the user.
    Calculates average score from quiz history and sends email report.
    """
    user_email = get_current_user(token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    logger.info(f"Preparing quiz score email for user: {user_email}")
    
    # Get quiz history to calculate average score
    try:
        if quiz_results_collection is None:
            logger.warning("Database unavailable, cannot fetch quiz history for email")
            return {"msg": "Email service temporarily unavailable"}
        
        results = list(quiz_results_collection.find({"user_email": user_email}))
        
        if not results:
            logger.info(f"No quiz results found for user {user_email}")
            return {"msg": "No quiz results available"}
        
        # Calculate average score
        total_score = sum(r.get("percentage", 0) for r in results)
        average_score = total_score / len(results)
        
        # Get completed topics
        completed_topics = list(set(r.get("topic", "") for r in results if r.get("topic")))
        
        # Send email
        email_sent = send_quiz_score_email(user_email, average_score, completed_topics)
        
        if email_sent:
            logger.info(f"Quiz score email sent successfully to {user_email}")
            return {
                "msg": "Quiz score email sent successfully",
                "average_score": round(average_score, 1),
                "total_quizzes": len(results),
                "completed_topics": len(completed_topics)
            }
        else:
            logger.error(f"Failed to send quiz score email to {user_email}")
            return {"msg": "Failed to send email. Please check email configuration."}
            
    except Exception as e:
        logger.error(f"Error sending quiz score email: {e}")
        return {"msg": "Error sending email"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

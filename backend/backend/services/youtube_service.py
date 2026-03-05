import os
import re
import logging
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_youtube_client():
    # Read key dynamically every time to support load_dotenv() and env var changes
    api_key = os.getenv("YOUTUBE_API_KEY") or YOUTUBE_API_KEY
    if not api_key:
        logger.error("YOUTUBE_API_KEY is not set in environment variables.")
        return None
    try:
        client = build("youtube", "v3", developerKey=api_key)
        logger.info("YouTube API client initialized successfully.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize YouTube API client: {e}")
        return None

def parse_duration(duration_str):
    if not duration_str: return 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match: return 0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

def fetch_youtube_videos(query: str, max_results: int = 5):
    logger.info(f"Fetching YouTube videos for query: {query}")
    youtube = get_youtube_client()
    
    # Placeholder results if API is down
    placeholder_results = [
        {
            "title": f"Mastering {query} - Concept Overview",
            "channel": "ExamBridge AI Tutor",
            "url": "https://www.youtube.com/results?search_query=" + query.replace(" ", "+"),
            "thumbnail": "https://img.youtube.com/vi/placeholder/hqdefault.jpg",
            "duration": "15:00",
            "score": 1000,
            "views": 5000,
            "likes": 250
        }
    ]

    if youtube is None:
        logger.warning("YouTube client not available. Returning placeholders.")
        return placeholder_results

    try:
        # 1. Primary Search - Professional Lectures
        search_query = f"{query} lecture gate"
        logger.info(f"Primary search: {search_query}")
        search = youtube.search().list(
            q=search_query,
            part="snippet", type="video",
            order="relevance", maxResults=max_results * 2
        ).execute()

        video_ids = [item['id']['videoId'] for item in search.get('items', [])]
        
        if not video_ids:
            logger.info("No videos found. Returning placeholders.")
            return placeholder_results

        # 2. Get Statistics
        videos_data = youtube.videos().list(
            part="statistics,contentDetails,snippet",
            id=",".join(video_ids)
        ).execute()

        scored_videos = []
        for item in videos_data.get('items', []):
            channel_name = item['snippet']['channelTitle']
            views = int(item['statistics'].get('viewCount', 0))
            likes = int(item['statistics'].get('likeCount', 0))
            
            scored_videos.append({
                "title": item['snippet']['title'],
                "channel": channel_name,
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "thumbnail": item['snippet']['thumbnails']['high']['url'],
                "duration": item['contentDetails']['duration'].replace('PT', '').lower(),
                "score": views + (likes * 10),
                "views": views,
                "likes": likes
            })

        scored_videos.sort(key=lambda x: x['score'], reverse=True)
        return scored_videos[:max_results]

    except Exception as e:
        logger.error(f"YouTube Fetch Error: {e}")
        return placeholder_results

def get_video_summary(video_id, topic, model, util):
    """
    Generates a memory-efficient extractive summary by ranking transcript sentences 
    relative to the target topic.
    """
    logger.info(f"Generating summary for video ID: {video_id} (Topic: {topic})")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t['text'] for t in transcript_list])
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', full_text) if len(s.strip()) > 20]
        
        if not sentences:
            logger.warning(f"No substantial content found in transcript for video {video_id}")
            return "Transcript available but no substantial content found for summary."

        # Encode topic and sentences
        topic_emb = model.encode(topic, convert_to_tensor=True)
        sentence_embs = model.encode(sentences, convert_to_tensor=True)
        
        # Compute similarities
        similarities = util.cos_sim(topic_emb, sentence_embs)[0]
        
        # Get top 3 most relevant sentences
        top_indices = similarities.argsort(descending=True)[:3]
        top_sentences = [sentences[idx] for idx in top_indices.tolist()]
        
        # Format summary
        summary = " • " + "\n • ".join(top_sentences)
        logger.info(f"Summary generated successfully for video {video_id}")
        return summary
    except Exception as e:
        logger.warning(f"Summary generation failed for video {video_id}: {e}")
        return "Summary not available (transcripts might be disabled for this video)."

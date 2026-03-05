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

def compute_like_ratio(likes, views):
    """Compute like ratio safely"""
    if views == 0:
        return 0.0
    return min(likes / views, 1.0)

def compute_title_relevance(title, topic):
    """
    Compute title relevance score (0-1).
    Higher score if topic keywords appear in title.
    """
    title_lower = title.lower()
    topic_lower = topic.lower()
    
    # Split topic into keywords
    keywords = [kw.strip() for kw in topic_lower.split() if len(kw.strip()) > 2]
    
    if not keywords:
        return 0.5
    
    # Count matching keywords
    matches = sum(1 for kw in keywords if kw in title_lower)
    
    # Return percentage of keywords matched, capped at 1.0
    return min(matches / len(keywords), 1.0)

def compute_duration_relevance(duration_seconds):
    """
    Compute duration relevance score (0-1).
    Optimal duration for educational content: 10-30 minutes.
    Penalize too short (<5 min) or too long (>90 min).
    """
    minutes = duration_seconds / 60
    
    if minutes < 5:
        return 0.3  # Too short, likely not comprehensive
    elif minutes < 10:
        return 0.7  # Somewhat short
    elif minutes <= 30:
        return 1.0  # Optimal range
    elif minutes <= 60:
        return 0.8  # Acceptable
    else:
        return 0.5  # Too long

def calculate_tubematix_score(video_data, topic, all_videos):
    """
    TubeMatix Scoring System for ranking educational YouTube videos.
    
    Score formula:
    TubeMatix = 0.4 * normalized_views + 0.3 * like_ratio + 0.2 * title_relevance + 0.1 * duration_relevance
    
    Args:
        video_data: dict with video metadata
        topic: str, the topic/query
        all_videos: list of all videos to normalize views against
    
    Returns:
        float: TubeMatix score (0-100)
    """
    # 1. Normalize views (0-1)
    if not all_videos:
        normalized_views = 0.0
    else:
        max_views = max([v.get('views', 0) for v in all_videos])
        if max_views == 0:
            normalized_views = 0.5
        else:
            normalized_views = video_data.get('views', 0) / max_views
    
    # 2. Like ratio
    likes = video_data.get('likes', 0)
    views = video_data.get('views', 1)
    like_ratio = compute_like_ratio(likes, views)
    
    # 3. Title relevance
    title = video_data.get('title', '')
    title_relevance = compute_title_relevance(title, topic)
    
    # 4. Duration relevance
    duration_str = video_data.get('duration', 'PT0S')
    duration_seconds = parse_duration(f"PT{duration_str}" if not duration_str.startswith('PT') else duration_str)
    duration_relevance = compute_duration_relevance(duration_seconds)
    
    # Calculate composite score (0-100)
    tubematix_score = (
        0.4 * normalized_views +
        0.3 * like_ratio +
        0.2 * title_relevance +
        0.1 * duration_relevance
    ) * 100
    
    logger.debug(f"TubeMatix Score for '{title[:50]}...': {tubematix_score:.1f} "
                f"(views:{normalized_views:.2f}, likes:{like_ratio:.2f}, title:{title_relevance:.2f}, duration:{duration_relevance:.2f})")
    
    return tubematix_score

def fetch_youtube_videos(query: str, max_results: int = 5):
    logger.info(f"Fetching YouTube videos for query: {query}")
    youtube = get_youtube_client()
    
    # Placeholder results if API is down
    placeholder_results = [
        {
            "title": f"Learn {query} - Complete Tutorial",
            "channel": "ExamBridge AI",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rickroll for testing
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            "duration": "3:32",
            "tubematix_score": 85.0,
            "views": 1500000,
            "likes": 75000,
            "id": "dQw4w9WgXcQ"
        },
        {
            "title": f"{query} Fundamentals - GATE Preparation",
            "channel": "GATE Academy",
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo
            "thumbnail": "https://img.youtube.com/vi/jNQXAC9IVRw/hqdefault.jpg",
            "duration": "0:18",
            "tubematix_score": 78.5,
            "views": 100000,
            "likes": 5000,
            "id": "jNQXAC9IVRw"
        },
        {
            "title": f"Advanced {query} Concepts",
            "channel": "Tech Tutorials",
            "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
            "thumbnail": "https://img.youtube.com/vi/kJQP7kiw5Fk/hqdefault.jpg",
            "duration": "4:42",
            "tubematix_score": 72.3,
            "views": 8000000,
            "likes": 400000,
            "id": "kJQP7kiw5Fk"
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
            duration_str = item['contentDetails']['duration']
            
            scored_videos.append({
                "title": item['snippet']['title'],
                "channel": channel_name,
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "thumbnail": item['snippet']['thumbnails']['high']['url'],
                "duration": duration_str.replace('PT', '').lower(),
                "views": views,
                "likes": likes,
                "id": item['id']
            })

        # Calculate TubeMatix scores
        for video in scored_videos:
            video['tubematix_score'] = calculate_tubematix_score(video, query, scored_videos)
            video['score'] = video['tubematix_score']  # Keep legacy score field
        
        # Sort by TubeMatix score
        scored_videos.sort(key=lambda x: x['tubematix_score'], reverse=True)
        return scored_videos[:max_results]

    except Exception as e:
        logger.error(f"YouTube Fetch Error: {e}")
        return placeholder_results

def fetch_and_rank_videos_by_topic(topic: str, max_results: int = 10, top_n: int = 3):
    """
    Fetch candidate videos for a topic and return the top-ranked videos using TubeMatix.
    
    Args:
        topic: str, the topic to search for
        max_results: int, number of candidate videos to fetch (default 10)
        top_n: int, number of top videos to return (default 3)
    
    Returns:
        list of top-ranked videos with TubeMatix scores
    """
    logger.info(f"Fetching and ranking videos for topic: {topic}")
    youtube = get_youtube_client()
    
    placeholder_results = [
        {
            "title": f"Learn {topic} - Complete Tutorial",
            "channel": "ExamBridge AI",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            "duration": "PT3M32S",
            "views": 1500000,
            "likes": 75000,
            "tubematix_score": 85.0,
            "id": "dQw4w9WgXcQ"
        },
        {
            "title": f"{topic} Fundamentals - GATE Preparation",
            "channel": "GATE Academy",
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "thumbnail": "https://img.youtube.com/vi/jNQXAC9IVRw/hqdefault.jpg",
            "duration": "PT0M18S",
            "views": 100000,
            "likes": 5000,
            "tubematix_score": 78.5,
            "id": "jNQXAC9IVRw"
        },
        {
            "title": f"Advanced {topic} Concepts",
            "channel": "Tech Tutorials",
            "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            "thumbnail": "https://img.youtube.com/vi/kJQP7kiw5Fk/hqdefault.jpg",
            "duration": "PT4M42S",
            "views": 8000000,
            "likes": 400000,
            "tubematix_score": 72.3,
            "id": "kJQP7kiw5Fk"
        }
    ]
    
    if youtube is None:
        logger.warning("YouTube client not available. Returning placeholders.")
        return placeholder_results[:top_n]
    
    try:
        # Search for videos
        search_query = f"{topic} educational gate exam"
        logger.info(f"Searching for: {search_query}")
        
        search_request = youtube.search().list(
            q=search_query,
            part="snippet",
            type="video",
            order="relevance",
            maxResults=max_results,
            relevanceLanguage="en"
        )
        search_response = search_request.execute()
        
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        
        if not video_ids:
            logger.warning(f"No videos found for topic: {topic}")
            return placeholder_results[:top_n]
        
        # Get full video details
        videos_request = youtube.videos().list(
            part="statistics,contentDetails,snippet",
            id=",".join(video_ids),
            maxResults=len(video_ids)
        )
        videos_response = videos_request.execute()
        
        videos_with_stats = []
        for item in videos_response.get('items', []):
            try:
                video_data = {
                    "id": item['id'],
                    "title": item['snippet']['title'],
                    "channel": item['snippet']['channelTitle'],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                    "thumbnail": item['snippet']['thumbnails']['high']['url'],
                    "duration": item['contentDetails']['duration'],
                    "views": int(item['statistics'].get('viewCount', 0)),
                    "likes": int(item['statistics'].get('likeCount', 0)),
                }
                videos_with_stats.append(video_data)
            except Exception as e:
                logger.warning(f"Error processing video {item.get('id', 'unknown')}: {e}")
                continue
        
        # Calculate TubeMatix scores for all videos
        for video in videos_with_stats:
            video['tubematix_score'] = calculate_tubematix_score(video, topic, videos_with_stats)
        
        # Sort by TubeMatix score (descending) and return top N
        videos_with_stats.sort(key=lambda x: x['tubematix_score'], reverse=True)
        
        result = videos_with_stats[:top_n]
        logger.info(f"Ranked and returning {len(result)} top videos for topic '{topic}'")
        
        return result if result else placeholder_results[:top_n]
        
    except Exception as e:
        logger.error(f"Error in fetch_and_rank_videos_by_topic: {e}")
        return placeholder_results[:top_n]

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

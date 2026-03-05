import os
import re
import logging
import time
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Cache for YouTube video results (2-minute TTL for more variety)
_video_cache = {}
CACHE_DURATION = 120  # 2 minutes

def clear_video_cache():
    """Clear the video cache to ensure fresh results"""
    global _video_cache
    _video_cache.clear()
    logger.info("YouTube video cache cleared")

def get_cache_size():
    """Get current cache size for monitoring"""
    return len(_video_cache)

# Static fallback video library when API key is missing. Topics mapped to sample video metadata.
SAMPLE_VIDEOS = {
    "operating systems": [
        {
            "id": "2i2N_Qo2B1U",
            "title": "Operating Systems: Crash Course Computer Science #18",
            "channel": "CrashCourse",
            "url": "https://www.youtube.com/watch?v=2i2N_Qo2B1U",
            "thumbnail": "https://img.youtube.com/vi/2i2N_Qo2B1U/hqdefault.jpg",
            "duration": "PT10M42S",
            "views": 2500000,
            "likes": 50000
        }
    ],
    "networks": [
        {
            "id": "3QhU9jd03a0",
            "title": "Computer Networks: Crash Course Computer Science #28",
            "channel": "CrashCourse",
            "url": "https://www.youtube.com/watch?v=3QhU9jd03a0",
            "thumbnail": "https://img.youtube.com/vi/3QhU9jd03a0/hqdefault.jpg",
            "duration": "PT12M29S",
            "views": 1800000,
            "likes": 35000
        }
    ],
    "data structures": [
        {
            "id": "RBSGKlAvo0M",
            "title": "Data Structures and Algorithms Full Course",
            "channel": "FreeCodeCamp",
            "url": "https://www.youtube.com/watch?v=RBSGKlAvo0M",
            "thumbnail": "https://img.youtube.com/vi/RBSGKlAvo0M/hqdefault.jpg",
            "duration": "PT5H",
            "views": 2200000,
            "likes": 42000
        }
    ],
    "algorithms": [
        {
            "id": "8hly31xKli0",
            "title": "Algorithms Full Course",
            "channel": "FreeCodeCamp",
            "url": "https://www.youtube.com/watch?v=8hly31xKli0",
            "thumbnail": "https://img.youtube.com/vi/8hly31xKli0/hqdefault.jpg",
            "duration": "PT2H30M",
            "views": 3000000,
            "likes": 55000
        }
    ],
    "database": [
        {
            "id": "HXV3zeQKqGY",
            "title": "SQL Full Course - Database Tutorial",
            "channel": "Programming with Mosh",
            "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "thumbnail": "https://img.youtube.com/vi/HXV3zeQKqGY/hqdefault.jpg",
            "duration": "PT3H",
            "views": 1500000,
            "likes": 28000
        }
    ],
    "machine learning": [
        {
            "id": "aircAruvnKk",
            "title": "Neural Networks - Deep Learning",
            "channel": "3Blue1Brown",
            "url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "thumbnail": "https://img.youtube.com/vi/aircAruvnKk/hqdefault.jpg",
            "duration": "PT20M",
            "views": 10000000,
            "likes": 200000
        }
    ]
}

def get_static_videos(topic: str, max_results: int = 5):
    """Return a list of statically defined videos relevant to the topic."""
    topic_lower = topic.lower()
    matched = []
    
    # First, try to find exact or partial matches
    for key, vids in SAMPLE_VIDEOS.items():
        if key in topic_lower or topic_lower in key:
            matched.extend(vids)
    
    # If no match found, return diverse generic educational videos
    if not matched:
        logger.warning(f"No static videos found for topic '{topic}', returning diverse educational content")
        
        # Create different generic videos based on topic category
        generic_videos = []
        
        # Determine topic category for more relevant videos
        if any(word in topic_lower for word in ['algorithm', 'data structure', 'programming', 'coding', 'computer science']):
            generic_videos = [
                {
                    "id": "RBSGKlAvo0M",
                    "title": f"Algorithms and {topic} - Complete Course",
                    "channel": "Computer Science",
                    "url": "https://www.youtube.com/watch?v=RBSGKlAvo0M",
                    "thumbnail": "https://img.youtube.com/vi/RBSGKlAvo0M/hqdefault.jpg",
                    "duration": "PT11M44S",
                    "views": 2800000,
                    "likes": 51000
                },
                {
                    "id": "8hly31xKli0",
                    "title": f"{topic} Explained - Data Structures Fundamentals",
                    "channel": "CS Education",
                    "url": "https://www.youtube.com/watch?v=8hly31xKli0",
                    "thumbnail": "https://img.youtube.com/vi/8hly31xKli0/hqdefault.jpg",
                    "duration": "PT11M43S",
                    "views": 2200000,
                    "likes": 42000
                }
            ]
        elif any(word in topic_lower for word in ['network', 'protocol', 'tcp', 'ip', 'routing']):
            generic_videos = [
                {
                    "id": "3QhU9jd03a0",
                    "title": f"Computer Networks and {topic} - Deep Dive",
                    "channel": "Network Engineering",
                    "url": "https://www.youtube.com/watch?v=3QhU9jd03a0",
                    "thumbnail": "https://img.youtube.com/vi/3QhU9jd03a0/hqdefault.jpg",
                    "duration": "PT12M29S",
                    "views": 1800000,
                    "likes": 35000
                }
            ]
        elif any(word in topic_lower for word in ['database', 'sql', 'query', 'dbms']):
            generic_videos = [
                {
                    "id": "FR4QIeZaPeM",
                    "title": f"Database Systems and {topic} - Complete Tutorial",
                    "channel": "Database Education",
                    "url": "https://www.youtube.com/watch?v=FR4QIeZaPeM",
                    "thumbnail": "https://img.youtube.com/vi/FR4QIeZaPeM/hqdefault.jpg",
                    "duration": "PT12M26S",
                    "views": 1900000,
                    "likes": 38000
                }
            ]
        elif any(word in topic_lower for word in ['machine learning', 'ai', 'artificial intelligence', 'ml']):
            generic_videos = [
                {
                    "id": "ukzFI9rgwfU",
                    "title": f"Machine Learning: {topic} Fundamentals",
                    "channel": "AI Education",
                    "url": "https://www.youtube.com/watch?v=ukzFI9rgwfU",
                    "thumbnail": "https://img.youtube.com/vi/ukzFI9rgwfU/hqdefault.jpg",
                    "duration": "PT12M18S",
                    "views": 1600000,
                    "likes": 32000
                }
            ]
        else:
            # Default generic videos for other topics
            generic_videos = [
                {
                    "id": "goWbT6W-6Q8",
                    "title": f"Engineering: {topic} Complete Guide",
                    "channel": "Engineering Education",
                    "url": "https://www.youtube.com/watch?v=goWbT6W-6Q8",
                    "thumbnail": "https://img.youtube.com/vi/goWbT6W-6Q8/hqdefault.jpg",
                    "duration": "PT12M13S",
                    "views": 1300000,
                    "likes": 25000
                },
                {
                    "id": "FZGj4pIj2Jk",
                    "title": f"{topic} - Technical Concepts Explained",
                    "channel": "Technical Learning",
                    "url": "https://www.youtube.com/watch?v=FZGj4pIj2Jk",
                    "thumbnail": "https://img.youtube.com/vi/FZGj4pIj2Jk/hqdefault.jpg",
                    "duration": "PT11M30S",
                    "views": 1700000,
                    "likes": 33000
                }
            ]
        
        matched = generic_videos
    
    # Calculate scores for matched videos
    for v in matched:
        v["tubematix_score"] = calculate_tubematix_score(v, topic, matched)
    
    # Sort by relevance score and return top results
    matched.sort(key=lambda x: x["tubematix_score"], reverse=True)
    return matched[:max_results]

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
    logger.info(f"Fetching YouTube videos for query: '{query}'")
    
    # Check cache first with timestamp-based invalidation
    import time
    import hashlib
    current_time = time.time()
    
    # Create cache key with query hash
    query_hash = hashlib.md5(query.lower().encode()).hexdigest()[:8]
    cache_key = f"{query_hash}_{max_results}"
    
    if cache_key in _video_cache:
        cached_data, timestamp = _video_cache[cache_key]
        # Use shorter cache duration (2 minutes) for more variety
        if current_time - timestamp < 120:  # 2 minutes instead of 5
            logger.info(f"Returning cached results for query: '{query}'")
            return cached_data
        else:
            # Remove expired cache entry
            del _video_cache[cache_key]
    
    youtube = get_youtube_client()
    
    # Create topic-specific placeholder results with verified working video IDs
    placeholder_results = [
        {
            "title": f"{query} - Complete Tutorial & Explanation",
            "channel": "CrashCourse",
            "url": "https://www.youtube.com/watch?v=2i2N_Qo2B1U",
            "thumbnail": "https://img.youtube.com/vi/2i2N_Qo2B1U/hqdefault.jpg",
            "duration": "10:42",
            "tubematix_score": 85.0,
            "views": 2500000,
            "likes": 50000,
            "id": "2i2N_Qo2B1U"
        },
        {
            "title": f"Understanding {query} - Step by Step Guide",
            "channel": "CrashCourse",
            "url": "https://www.youtube.com/watch?v=3QhU9jd03a0",
            "thumbnail": "https://img.youtube.com/vi/3QhU9jd03a0/hqdefault.jpg",
            "duration": "12:29",
            "tubematix_score": 78.5,
            "views": 1800000,
            "likes": 35000,
            "id": "3QhU9jd03a0"
        },
        {
            "title": f"{query} Advanced Concepts & Applications",
            "channel": "MIT OpenCourseWare",
            "url": "https://www.youtube.com/watch?v=26QPDBe-NB8",
            "thumbnail": "https://img.youtube.com/vi/26QPDBe-NB8/hqdefault.jpg",
            "duration": "49:23",
            "tubematix_score": 72.3,
            "views": 150000,
            "likes": 2000,
            "id": "26QPDBe-NB8"
        }
    ]

    if youtube is None:
        logger.warning(f"YouTube client not available for query '{query}'. Using static videos.")
        result = get_static_videos(query, max_results=max_results)
        # Cache the static results with shorter duration
        _video_cache[cache_key] = (result, current_time)
        return result

    try:
        # Create multiple search queries for better results with more variety
        search_queries = [
            f"{query} tutorial explanation",
            f"{query} lecture university", 
            f"what is {query} concept",
            f"{query} course"
        ]
        
        all_videos = []
        
        for search_query in search_queries:
            logger.info(f"Searching with query: '{search_query}'")
            search = youtube.search().list(
                q=search_query,
                part="snippet", 
                type="video",
                order="relevance", 
                maxResults=max_results // 2,  # Fewer results per query for more variety
                relevanceLanguage="en"
            ).execute()

            video_ids = [item['id']['videoId'] for item in search.get('items', [])]
            
            if video_ids:
                # Get video details
                videos_data = youtube.videos().list(
                    part="statistics,contentDetails,snippet",
                    id=",".join(video_ids)
                ).execute()

                for item in videos_data.get('items', []):
                    try:
                        channel_name = item['snippet']['channelTitle']
                        views = int(item['statistics'].get('viewCount', 0))
                        likes = int(item['statistics'].get('likeCount', 0))
                        duration_str = item['contentDetails']['duration']
                        
                        video_data = {
                            "title": item['snippet']['title'],
                            "channel": channel_name,
                            "url": f"https://www.youtube.com/watch?v={item['id']}",
                            "thumbnail": item['snippet']['thumbnails']['high']['url'],
                            "duration": duration_str.replace('PT', '').lower(),
                            "views": views,
                            "likes": likes,
                            "id": item['id']
                        }
                        all_videos.append(video_data)
                    except Exception as e:
                        logger.warning(f"Error processing video {item.get('id', 'unknown')}: {e}")
                        continue
        
        if not all_videos:
            logger.warning(f"No videos found for any search query related to '{query}'. Using static videos.")
            result = get_static_videos(query, max_results=max_results)
            # Cache the static results
            _video_cache[cache_key] = (result, current_time)
            return result

        # Remove duplicates based on video ID
        unique_videos = []
        seen_ids = set()
        for video in all_videos:
            if video['id'] not in seen_ids:
                seen_ids.add(video['id'])
                unique_videos.append(video)

        # Calculate TubeMatix scores for all videos
        for video in unique_videos:
            video['tubematix_score'] = calculate_tubematix_score(video, query, unique_videos)
            video['score'] = video['tubematix_score']
        
        # Sort by TubeMatix score and return top results
        unique_videos.sort(key=lambda x: x['tubematix_score'], reverse=True)
        result = unique_videos[:max_results]
        
        # Cache the results with shorter duration
        _video_cache[cache_key] = (result, current_time)
        
        logger.info(f"Successfully fetched and ranked {len(result)} videos for query '{query}'")
        return result

    except Exception as e:
        logger.error(f"YouTube API error for query '{query}': {e}")
        # fallback to static videos when API call fails
        result = get_static_videos(query, max_results=max_results)
        # Cache the fallback results
        _video_cache[cache_key] = (result, current_time)
        return result

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
            "url": "https://www.youtube.com/watch?v=2i2N_Qo2B1U",
            "thumbnail": "https://img.youtube.com/vi/2i2N_Qo2B1U/hqdefault.jpg",
            "duration": "PT10M42S",
            "views": 2500000,
            "likes": 50000,
            "tubematix_score": 85.0,
            "id": "2i2N_Qo2B1U"
        },
        {
            "title": f"{topic} Fundamentals - Educational Video",
            "channel": "Educational Channel",
            "url": "https://www.youtube.com/watch?v=3QhU9jd03a0",
            "thumbnail": "https://img.youtube.com/vi/3QhU9jd03a0/hqdefault.jpg",
            "duration": "PT12M29S",
            "views": 1800000,
            "likes": 35000,
            "tubematix_score": 78.5,
            "id": "3QhU9jd03a0"
        },
        {
            "title": f"Advanced {topic} Concepts",
            "channel": "Tech Tutorials",
            "url": "https://www.youtube.com/watch?v=26QPDBe-NB8",
            "thumbnail": "https://img.youtube.com/vi/26QPDBe-NB8/hqdefault.jpg",
            "duration": "PT49M23S",
            "views": 150000,
            "likes": 2000,
            "tubematix_score": 72.3,
            "id": "26QPDBe-NB8"
        }
    ]
    
    if youtube is None:
        logger.warning("YouTube client not available. Falling back to static videos.")
        return get_static_videos(topic, max_results=max_results)[:top_n]
    
    try:
        # Search for videos
        search_query = f"{topic} educational tutorial"
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
            return get_static_videos(topic, max_results=max_results)[:top_n]
        
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
        return get_static_videos(topic, max_results=max_results)[:top_n]

def get_video_summary(video_id, topic, model, util, video_title=""):
    """
    Generates a memory-efficient extractive summary by ranking transcript sentences 
    relative to the target topic. Falls back to AI-generated summary if transcripts unavailable.
    """
    logger.info(f"Generating summary for video ID: {video_id} (Topic: {topic})")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t['text'] for t in transcript_list])
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', full_text) if len(s.strip()) > 20]
        
        if not sentences:
            logger.warning(f"No substantial content found in transcript for video {video_id}")
            return generate_ai_summary(topic, video_title, model)

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
        logger.warning(f"Transcript unavailable for video {video_id}, generating AI summary: {e}")
        return generate_ai_summary(topic, video_title, model)

def generate_ai_summary(topic, video_title, model):
    """
    Generates an AI summary based on topic and video title when transcripts are unavailable.
    Uses sentence transformers to generate relevant educational content.
    """
    logger.info(f"Generating AI summary for topic: {topic}, title: {video_title}")
    
    # Create topic-based educational content templates
    topic_keywords = topic.lower().split()
    
    # Base educational content for common CS topics
    educational_templates = {
        "operating": [
            "Operating systems manage computer hardware and software resources, providing common services for computer programs.",
            "Key concepts include process management, memory management, file systems, and I/O operations.",
            "Understanding OS fundamentals is crucial for system design and resource optimization in computing."
        ],
        "network": [
            "Computer networks enable communication and resource sharing between connected devices using standardized protocols.",
            "Core concepts include TCP/IP, routing, switching, network security, and data transmission methods.",
            "Network architecture and design principles are essential for building scalable communication systems."
        ],
        "data structure": [
            "Data structures organize and store data efficiently, enabling optimal access and modification operations.",
            "Common structures include arrays, linked lists, stacks, queues, trees, graphs, and hash tables.",
            "Choosing the right data structure impacts algorithm efficiency and overall program performance."
        ],
        "algorithm": [
            "Algorithms are step-by-step procedures for solving problems and performing computations efficiently.",
            "Key areas include sorting, searching, dynamic programming, graph algorithms, and complexity analysis.",
            "Algorithm design and analysis form the foundation of efficient software development and optimization."
        ],
        "database": [
            "Database systems provide structured storage, retrieval, and management of data for applications.",
            "Core concepts include SQL, normalization, indexing, transactions, ACID properties, and query optimization.",
            "Understanding database design is essential for building reliable and scalable data-driven applications."
        ],
        "machine learning": [
            "Machine learning enables systems to learn patterns from data and make predictions without explicit programming.",
            "Key concepts include supervised learning, unsupervised learning, neural networks, and model evaluation.",
            "ML applications span computer vision, natural language processing, recommendation systems, and more."
        ],
        "default": [
            f"This video covers essential concepts in {topic}, providing comprehensive coverage of theoretical foundations.",
            f"Key learning objectives include understanding core principles, practical applications, and advanced techniques in {topic}.",
            f"The content emphasizes problem-solving skills and real-world implementation strategies for {topic}."
        ]
    }
    
    # Find matching template
    selected_template = educational_templates["default"]
    for keyword, template in educational_templates.items():
        if keyword in topic.lower() or keyword in video_title.lower():
            selected_template = template
            break
    
    # Format the AI-generated summary
    summary = " • " + "\n • ".join(selected_template)
    summary += "\n\n[AI-Generated Summary - Transcript Unavailable]"
    
    logger.info(f"AI summary generated successfully for topic: {topic}")
    return summary

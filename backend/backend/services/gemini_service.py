import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import Gemini, but don't fail if it's not installed
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Gemini features disabled.")

# Configure Gemini API
def configure_gemini():
    """Configure Gemini API with environment variable"""
    if not GEMINI_AVAILABLE:
        return False
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set in environment variables")
        return False
    
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        return False

def generate_topic_summary(topic: str, max_words: int = 300) -> Optional[str]:
    """
    Generate an AI summary for a topic using Gemini.
    
    Args:
        topic: The topic to summarize
        max_words: Maximum words for the summary
    
    Returns:
        Generated summary text or None if generation fails
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini not available, using fallback summary")
        return generate_fallback_summary(topic)
    
    if not configure_gemini():
        return generate_fallback_summary(topic)
    
    try:
        # Use gemini-pro model
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Generate a comprehensive educational summary for the topic "{topic}".

The summary should include:
1. Key concepts and definitions
2. Important principles and theories
3. Practical applications
4. Learning objectives
5. Common exam questions or important points to remember

Format the summary in clear sections with bullet points.
Keep it under {max_words} words.
Make it suitable for GATE exam preparation.
"""
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            logger.info(f"Gemini summary generated for topic: {topic}")
            return response.text
        else:
            logger.warning("Gemini returned empty response")
            return generate_fallback_summary(topic)
            
    except Exception as e:
        logger.error(f"Error generating Gemini summary: {e}")
        return generate_fallback_summary(topic)

def generate_fallback_summary(topic: str) -> str:
    """Generate a fallback summary when Gemini is unavailable"""
    return f"""Summary for {topic}:

• Key Concepts:
  - Fundamental principles and core ideas
  - Important terminology and definitions
  - Basic concepts to understand before advanced topics

• Learning Objectives:
  - Understand theoretical foundations
  - Apply concepts to solve problems
  - Analyze and evaluate different approaches

• Practical Applications:
  - Real-world use cases
  - Industry applications
  - GATE exam relevance

• Important Points:
  - Focus on understanding rather than memorization
  - Practice with previous year questions
  - Create notes for quick revision

[AI-Generated Summary - Powered by ExamBridge AI]
"""

# Global configuration status
_gemini_configured = False

def is_gemini_available() -> bool:
    """Check if Gemini is available and configured"""
    global _gemini_configured
    if not _gemini_configured and GEMINI_AVAILABLE:
        _gemini_configured = configure_gemini()
    return _gemini_configured

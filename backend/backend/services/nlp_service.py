import pdfplumber
import io
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy load heavy modules to prevent startup issues
_model = None
_util = None
_model_loading = False

def get_model():
    global _model, _model_loading
    if _model is None and not _model_loading:
        _model_loading = True
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            _model_loading = False
            raise RuntimeError(f"Model loading failed: {e}")
        finally:
            _model_loading = False
    elif _model_loading:
        # Wait for model to finish loading if another thread is loading it
        import time
        while _model_loading:
            time.sleep(0.1)
    return _model

def get_util():
    global _util
    if _util is None:
        try:
            from sentence_transformers import util
            _util = util
            logger.info("Sentence transformers utility loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load sentence_transformers.util: {e}")
            raise RuntimeError(f"Utility loading failed: {e}")
    return _util

# Preload model at startup
def preload_models():
    """Preload models to reduce first request latency"""
    try:
        logger.info("Preloading NLP models...")
        get_model()
        get_util()
        logger.info("NLP models preloaded successfully.")
    except Exception as e:
        logger.warning(f"Model preloading failed: {e}. Will load on first request.")

def extract_text_from_pdf(contents: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"Starting PDF extraction for {total_pages} pages")
            
            # Early termination if PDF is too large
            if total_pages > 100:
                logger.warning(f"PDF has {total_pages} pages, which may cause delays. Processing first 50 pages.")
                max_pages = 50
            else:
                max_pages = total_pages
            
            for page_num, page in enumerate(pdf.pages[:max_pages], 1):
                try:
                    # Use faster text extraction with some optimizations
                    extracted = page.extract_text(
                        layout=True,
                        x_tolerance=1,
                        y_tolerance=1
                    )
                    
                    if extracted and len(extracted.strip()) > 10:  # Skip pages with minimal text
                        text += extracted + " "
                    
                    # Log progress every 10 pages for debugging
                    if page_num % 10 == 0:
                        logger.info(f"Processed {page_num}/{min(max_pages, total_pages)} pages")
                        
                except Exception as page_error:
                    logger.warning(f"Error extracting page {page_num}: {page_error}")
                    continue  # Skip problematic pages and continue
            
            # Clean up memory
            pdf.close()
            
            logger.info(f"PDF extraction completed. Extracted {len(text)} characters from {min(max_pages, total_pages)} pages")
            
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        raise ValueError(f"PDF extraction failed: {e}")
    
    # Validate extracted text
    if not text or len(text.strip()) < 50:
        raise ValueError("Extracted text is too short or empty. Please check if the PDF contains readable text.")
    
    # Limit text length to prevent memory issues
    if len(text) > 50000:  # Limit to ~50k characters
        text = text[:50000]
        logger.info("Text truncated to 50,000 characters to prevent memory issues.")
    
    return text.strip()

def extract_topics(text):
    if not text:
        return []
    # Clean text and split by newlines
    lines = text.split("\n")
    # Filter lines that look like topics (length check + no page numbers)
    topics = [line.strip() for line in lines if 10 < len(line.strip()) < 150 and not re.search(r'page \d+', line, re.I)]
    # Deduplicate while preserving order
    return list(dict.fromkeys(topics))

def compute_overall_similarity(text1, text2):
    logger.info("Computing overall similarity...")
    model = get_model()
    util = get_util()
    embeddings = model.encode([text1, text2])
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    score = float(similarity[0][0]) * 100
    logger.info(f"Overall similarity computed: {score:.2f}%")
    return score

def topic_wise_similarity_ranking(college_topics, gate_topics):
    if not college_topics or not gate_topics:
        logger.warning("Empty topics provided for comparison.")
        return []
        
    logger.info(f"Starting topic-wise comparison (GATE topics: {len(gate_topics)}, College topics: {len(college_topics)})")
    model = get_model()
    util = get_util()
    
    # Batch encode for performance
    college_embeddings = model.encode(college_topics, convert_to_tensor=True)
    gate_embeddings = model.encode(gate_topics, convert_to_tensor=True)
    
    # Compute similarity matrix
    similarity_matrix = util.cos_sim(gate_embeddings, college_embeddings)
    
    results = []
    for i, gate_topic in enumerate(gate_topics):
        # Find best match in college syllabus
        best_index = similarity_matrix[i].argmax()
        best_score = float(similarity_matrix[i][best_index]) * 100
        matched_topic = college_topics[best_index]
        
        # Priority logic
        if best_score < 40:
            priority = "🚨 High"
        elif 40 <= best_score < 70:
            priority = "🟡 Medium"
        else:
            priority = "✅ Low"
            
        results.append({
            "gate_topic": gate_topic,
            "matched_topic": matched_topic,
            "similarity": round(best_score, 1),
            "priority": priority
        })
        
    # Sort by priority and then similarity (Critical gaps first)
    results.sort(key=lambda x: (x["priority"] != "🚨 High", x["priority"] != "🟡 Medium", x["similarity"]))
    logger.info("Topic-wise comparison completed.")
    return results

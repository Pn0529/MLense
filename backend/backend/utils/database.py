import os
import certifi
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use environment variable for MongoDB Atlas or fall back to local
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Initialize client and collections as None by default
client = None
db = None
users_collection = None
analyses_collection = None
gate_topics_collection = None
pyqs_collection = None
quiz_results_collection = None

try:
    # Set a short timeout for the initial connection attempt
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
    client.server_info() # Test connection
    logger.info("✅ MongoDB Connected successfully!")

    db = client["exambridge"]
    users_collection = db["users"]
    analyses_collection = db["analyses"]
    gate_topics_collection = db["gate_topics"]
    pyqs_collection = db["pyqs"]
    quiz_results_collection = db["quiz_results"]
    logger.info("MongoDB collections initialized.")

except Exception as e:
    logger.error(f"⚠️ MongoDB Connection Error: {e}")
    logger.warning("Backend will continue running without persistence. Collections will be None.")
    # Fallback placeholders to prevent startup crash
    # client, db, and collections remain None as initialized above.
    # If a connection was partially established, ensure client is closed if not fully functional
    if client:
        try:
            client.close()
            logger.info("Partially connected MongoDB client closed.")
        except Exception as close_e:
            logger.error(f"Error closing partially connected MongoDB client: {close_e}")

# The collections are now either properly initialized or None,
# allowing the application to check for their existence before use.
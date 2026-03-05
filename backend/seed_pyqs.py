"""
Seed script to populate the 'pyqs' collection in MongoDB with GATE PYQs.
Run this once: python seed_pyqs.py
"""
import os, sys, certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env from the backend folder
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))
# Also try the direct path
load_dotenv('c:/Users/varsh/MLense/Exam/backend/.env')

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Add parent to path so we can import the pyqs data
sys.path.insert(0, os.path.dirname(__file__))
from backend.data.pyqs import GATE_PYQS

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
db = client["exambridge"]
pyqs_col = db["pyqs"]

# Clear existing data
pyqs_col.delete_many({})
print("Cleared existing PYQs from database.")

# Insert each category as a document
total_questions = 0
for category, questions in GATE_PYQS.items():
    doc = {
        "category": category,
        "questions": questions
    }
    pyqs_col.insert_one(doc)
    total_questions += len(questions)
    print(f"  ✅ Inserted '{category}' with {len(questions)} questions")

print(f"\n🎉 Successfully seeded {len(GATE_PYQS)} categories with {total_questions} questions into MongoDB!")

# Verify
count = pyqs_col.count_documents({})
print(f"📊 Verification: {count} documents in pyqs collection.")

client.close()

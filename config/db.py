import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is required to connect to the career database")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client["icehacks"]

users = db["users"]
career_profiles = db["career_profiles"]
career_learning = db["career_learning"]
persistent_sessions = db["persistent_sessions"]
career_feedback = db["career_feedback"]

# Enforce one account per email and one profile per account.
users.create_index("email", unique=True)
career_profiles.create_index("user_id", unique=True)
career_learning.create_index("user_id", unique=True)
persistent_sessions.create_index("token_hash", unique=True)
persistent_sessions.create_index("user_id")
persistent_sessions.create_index("expires_at", expireAfterSeconds=0)
career_feedback.create_index(
    [("user_id", 1), ("submission_id", 1)],
    unique=True,
)
career_feedback.create_index([("training_consent", 1), ("created_at", 1)])

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Resolve .env relative to the project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

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

# Enforce one account per email and one profile per account.
users.create_index("email", unique=True)
career_profiles.create_index("user_id", unique=True)
career_learning.create_index("user_id", unique=True)
"""Shared database connection and dependencies for all route modules."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
import certifi

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (singleton) with production-safe timeouts
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    socketTimeoutMS=30000,
    tlsCAFile=certifi.where(),
)
db = client[os.environ['DB_NAME']]

# GridFS for file storage (recordings, media)
fs_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="media_files")

logger = logging.getLogger(__name__)

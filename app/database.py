import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Motor is an async library for MongoDB that helps perform
# database operations asynchronously, suitable for applications 
# that use async/await like FastAPI.
client = AsyncIOMotorClient(MONGO_URI)
db = client.task_manager

# Collections
users_collection = db.users
tasks_collection = db.tasks

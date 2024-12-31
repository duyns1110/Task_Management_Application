from .database import users_collection, tasks_collection
from .schemas import UserCreate, TaskCreate, TaskUpdate
from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime
from .models import Utils
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
    }

def task_helper(task) -> dict:
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description"),
        "due_date": task.get("due_date"),
        "status": task["status"],
        "created_at": Utils.format_datetime(task["created_at"]),
        "updated_at": Utils.format_datetime(task["updated_at"]),
    }

async def create_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    user_doc = {"username": user.username, "password": hashed_password}
    result = await users_collection.insert_one(user_doc)
    new_user = await users_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

async def get_user_by_username(username: str):
    user = await users_collection.find_one({"username": username})
    return user

async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    return None

# Task CRUD
async def create_task(user_id: str, task: TaskCreate):
    task_doc = {
        "user_id": ObjectId(user_id),
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "status": task.status,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await tasks_collection.insert_one(task_doc)
    new_task = await tasks_collection.find_one({"_id": result.inserted_id})
    return task_helper(new_task)


async def get_tasks(user_id: str, limit: int = 10) -> List[dict]:
    tasks = []
    cursor = tasks_collection.find({"user_id": ObjectId(user_id)}).sort("updated_at", -1).limit(limit)
    async for task in cursor:
        tasks.append(task_helper(task))
    return tasks

async def get_task(task_id: str, user_id: str):
    task = await tasks_collection.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
    if task:
        return task_helper(task)
    return None

async def update_task(task_id: str, user_id: str, task: TaskUpdate):
    update_data = {k: v for k, v in task.dict().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await tasks_collection.update_one(
            {"_id": ObjectId(task_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
        )
    updated_task = await tasks_collection.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
    if updated_task:
        return task_helper(updated_task)
    return None

async def delete_task(task_id: str, user_id: str):
    result = await tasks_collection.delete_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
    return result.deleted_count > 0

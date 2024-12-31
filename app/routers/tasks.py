from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from ..schemas import TaskCreate, TaskOut, TaskUpdate
from ..crud import create_task, get_tasks, get_task, update_task, delete_task
from ..dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskOut)
async def add_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    new_task = await create_task(current_user["id"], task)
    return new_task

@router.get("/", response_model=List[TaskOut])
async def read_tasks(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to retrieve")
    ):
    tasks = await get_tasks(current_user["id"], limit)
    return tasks

@router.get("/{task_id}", response_model=TaskOut)
async def read_task(task_id: str, current_user: dict = Depends(get_current_user)):
    task = await get_task(task_id, current_user["id"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskOut)
async def modify_task(task_id: str, task: TaskUpdate, current_user: dict = Depends(get_current_user)):
    updated_task = await update_task(task_id, current_user["id"], task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/{task_id}")
async def remove_task(task_id: str, current_user: dict = Depends(get_current_user)):
    success = await delete_task(task_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}

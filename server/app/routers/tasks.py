from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import Tasks
from ..schemas import TaskCreate, TaskResponse
from ..dependencies import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    new_task = Tasks(
        title=task.title,
        description=task.description,
        priority=task.priority,
        user_id=user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/", response_model=list[TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Tasks).filter(Tasks.user_id == user.id).all()


@router.put("/{task_id}", response_model=TaskResponse)
def mark_complete(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    task = db.query(Tasks).filter(
        Tasks.id == task_id,
        Tasks.user_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.complete = True
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    task = db.query(Tasks).filter(
        Tasks.id == task_id,
        Tasks.user_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}

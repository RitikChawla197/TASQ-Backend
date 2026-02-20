from datetime import datetime

from fastapi import HTTPException, Response
from sqlalchemy.orm import Session, joinedload

from src.tasks.dtos import TaskSchema, TaskUpdateSchema
from src.tasks.models import TaskModel
from src.users.models import Project


def create_task(body: TaskSchema, db: Session):
    data = body.model_dump()
    data.pop("assigned_user_name", None)

    new_task = TaskModel(**data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_all_tasks(db: Session, project_name: str = None):
    query = db.query(TaskModel)

    if project_name:
        query = query.join(Project).filter(Project.name == project_name)

    return query.all()


def get_projects_by_name(db: Session, project_name: str):
    return db.query(TaskModel).join(Project).filter(Project.name == project_name).all()


def update_task_by_name(body: TaskUpdateSchema, db: Session):
    if not body.id:
        raise HTTPException(status_code=400, detail="Task ID is required in the body to update.")

    task = db.query(TaskModel).filter(TaskModel.id == body.id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {body.id} not found.")

    data = body.model_dump(exclude_unset=True)
    data.pop("id", None)
    data.pop("assigned_user_name", None)
    data.pop("created_at", None)

    for key, value in data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now()
    db.commit()
    db.refresh(task)
    return task


def get_tasks_by_department(department_name: str, db: Session):
    return (
        db.query(TaskModel)
        .join(Project)
        .options(
            joinedload(TaskModel.assigned_user),
            joinedload(TaskModel.project),
        )
        .filter(Project.department == department_name)
        .all()
    )


def delete_task(task_id: int, db: Session):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    db.delete(task)
    db.commit()
    return Response(status_code=204)


def get_task_by_id(task_id: int, db: Session):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


def update_task(task_id: int, body: TaskSchema, db: Session):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    body_data = body.model_dump()
    body_data.pop("created_at", None)

    for key, value in body_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now()
    db.commit()
    db.refresh(task)
    return task

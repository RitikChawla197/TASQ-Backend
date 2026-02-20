from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.tasks import controller
from src.tasks.dtos import TaskSchema, TaskResponseSchema, TaskUpdateSchema
from src.utils.db import get_db


task_routes = APIRouter(prefix="/tasks", tags=["tasks"])


@task_routes.post("/create_task", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskSchema, db: Session = Depends(get_db)):
    return controller.create_task(body, db)


@task_routes.get("/all_tasks", response_model=List[TaskResponseSchema], status_code=status.HTTP_200_OK)
def get_all_tasks(project_name: Optional[str] = None, db: Session = Depends(get_db)):
    return controller.get_all_tasks(db, project_name)


@task_routes.get("/task_by_name/{project_name}", response_model=List[TaskResponseSchema], status_code=status.HTTP_200_OK)
def get_tasks_by_project_name(project_name: str, db: Session = Depends(get_db)):
    return controller.get_projects_by_name(db, project_name)


@task_routes.put("/update_by_name", response_model=TaskResponseSchema, status_code=status.HTTP_200_OK)
def update_task_by_name(body: TaskUpdateSchema, db: Session = Depends(get_db)):
    return controller.update_task_by_name(body, db)


@task_routes.delete("/delete/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    return controller.delete_task(task_id, db)


@task_routes.get("/by_department/{department}", response_model=List[TaskResponseSchema], status_code=status.HTTP_200_OK)
def get_tasks_by_department(department: str, db: Session = Depends(get_db)):
    return controller.get_tasks_by_department(department, db)


@task_routes.get("/task/{id}", response_model=TaskResponseSchema, status_code=status.HTTP_200_OK)
def get_task_by_id(id: int, db: Session = Depends(get_db)):
    return controller.get_task_by_id(id, db)


@task_routes.put("/update_task/{id}", response_model=TaskResponseSchema, status_code=status.HTTP_200_OK)
def update_task(id: int, body: TaskSchema, db: Session = Depends(get_db)):
    return controller.update_task(id, body, db)


@task_routes.delete("/delete_task/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_task_legacy(id: int, db: Session = Depends(get_db)):
    return controller.delete_task(id, db)

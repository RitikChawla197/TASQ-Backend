from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,Enum as SAEnum
from src.utils.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from src.tasks.dtos import TaskStatus, TaskPriority # Import Enums

class TaskModel(Base):
    __tablename__ = "user_tasks"
    id = Column[int](Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column[bool](Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SAEnum(TaskPriority), default=TaskPriority.MEDIUM)
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    # Foreign Key to Projects
    project_id = Column(Integer, ForeignKey("projects.id"))
    assigned_user_id = Column(Integer, ForeignKey("users.id")) # Assuming you have a users table
    # Optional: Relationship for easy access
    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("UserModel")
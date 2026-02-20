from pydantic import BaseModel,Field, computed_field
from datetime import datetime
from typing import Optional
from enum import Enum

class UserInner(BaseModel):
    name: str

# --- 1. Define Enums (These were missing!) ---
class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    BACKLOG = "BACKLOG"
    REVIEW = "REVIEW"
    

class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# --- 2. Update TaskSchema (Input) ---
class TaskSchema(BaseModel):
    title: str
    description: Optional[str] = None
    
    # New Fields
    project_id: int
    assigned_user_id: int
    status: TaskStatus = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    completed: bool = False # Kept for backward compatibility if needed
    
    # Use default_factory for dynamic times, or allow None if DB handles it
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None
    assigned_user: Optional[UserInner] = Field(default=None, exclude=True)
    @computed_field
    def assigned_user_name(self) -> str | None:
        if self.assigned_user:
            return self.assigned_user.name
        return None


class TaskUpdateSchema(BaseModel):
    # Standard Editable Fields
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    completed: Optional[bool] = None
    
    # Date Fields
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    # Optional: Allow manual editing of creation time (e.g. for backdating)
    created_at: Optional[datetime] = None

#     class Config:
#         from_attributes = True
# class TaskSchema(BaseModel):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None
    
#     # --- STEP A: The "Bridge" Field ---
#     # This field tells Pydantic: "Read the assigned_user relationship from the DB"
#     # exclude=True tells Pydantic: "Do NOT show this whole object in the final JSON"
#     assigned_user: Optional[UserInner] = Field(default=None, exclude=True)

#     # --- STEP B: The Computed Name ---
#     # This takes the object from Step A and just grabs the string name
#     @computed_field
#     def assigned_user_name(self) -> str | None:
#         if self.assigned_user:
#             return self.assigned_user.name
#         return None

# --- 3. Update TaskResponseSchema (Output) ---
# class TaskResponseSchema(TaskSchema):
#     id: int
    # You can override specific fields if needed, 
    # but inheriting from TaskSchema includes all the fields above automatically.
 
 
# 1. Define a tiny helper for Project (just to capture the name)
class ProjectInner(BaseModel):
    name: str
       
    
class TaskResponseSchema(TaskSchema):
    id: int
    
    # --- Hidden Fields (Fetched from DB but hidden from JSON) ---
    assigned_user: Optional[UserInner] = Field(default=None, exclude=True)
    project: Optional[ProjectInner] = Field(default=None, exclude=True) # <--- Add this

    # --- Visible Computed Fields ---
    @computed_field
    def assigned_user_name(self) -> str | None:
        if self.assigned_user:
            return self.assigned_user.name
        return None

    @computed_field
    def project_name(self) -> str | None: # <--- Add this function
        if self.project:
            return self.project.name
        return None    
    
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    MANAGER = "manager"
    EMPLOYEE = "employee"

class UserSchema(BaseModel):
    name : str
    username : str
    password : str
    email : str 
    role: UserRole
    department: str

class UserResponseSchema(BaseModel):
    name : str
    username : str
    email : str   
    id : int  
    department: str

class LoginSchema(BaseModel):
    username : str
    password : str
    
class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    department: Optional[str] = None  # <--- Make this Optional to fix the error
    owner_id: int

    class Config:
        from_attributes = True
        
        
class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None

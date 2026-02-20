# from sqlalchemy import Column, String, Integer,ForeignKey, DateTime, Boolean
# from sqlalchemy.orm import relationship
# from src.utils.db import Base

# class UserModel(Base):
#     __tablename__ = "User"

#     id = Column(Integer,primary_key=True)   
#     name = Column[str](String,nullable=False)
#     username = Column[str](String,nullable=False)
#     hash_password = Column(String,nullable=False)
#     email = Column(String)
#     role = Column(String)  # e.g., "manager", "employee"
#     department = Column(String)  # e.g., "IT", "Sales", "HR"

#     # Relationship to projects (optional, for fetching all projects created by user)
#     projects = relationship("Project", back_populates="owner")
    
# # Project Model linked to a Department
# class Project(Base):
#     __tablename__ = "projects"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), index=True)
#     description = Column(String)
#     department = Column(String)  # The department this project belongs to
#     owner_id = Column(Integer, ForeignKey("User.id"))

#     owner = relationship("UserModel", back_populates="projects")  

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.utils.db import Base # Assuming this is your setup

class UserModel(Base):
    __tablename__ = "users" # Ideally, table names should be lowercase plural like 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False) # Good practice to limit length here too
    username = Column(String(255), nullable=False, unique=True)
    hash_password = Column(String(255), nullable=False)
    email = Column(String(255))
    role = Column(String(50)) 
    department = Column(String(100))

    # Relationship to projects
    # Note: "Project" string refers to the class name below
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True) 
    description = Column(String(1000)) 
    department = Column(String(100)) 
    
    owner_id = Column(Integer, ForeignKey("users.id")) 

    # Relationship uses Class Name
    owner = relationship("UserModel", back_populates="projects")
    tasks = relationship("TaskModel", back_populates="project")
from src.users.dtos import UserSchema,LoginSchema,ProjectCreate,ProjectUpdateSchema
from sqlalchemy.orm import Session
from src.users.models import UserModel,Project
from fastapi import HTTPException,status,Request,Depends,Response
from pwdlib import PasswordHash
import jwt 
from src.utils.settings import settings
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError
from src.utils.db import get_db # You need to import your DB dependency
from typing import List
from src.tasks.models import TaskModel
from sqlalchemy import or_

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password,hash_password):
    return password_hash.verify(plain_password,hash_password)

# --- Auth Dependency ---
# This function is designed to be used with Depends() in the ROUTER
def get_current_user(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized")
        
        # Handle "Bearer <token>" format if present
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = data.get("_id")

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return user
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def register(body:UserSchema,db:Session):
    is_user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if is_user:
        raise HTTPException(400,detail="username already exist")

    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(400,detail="email already exist")
    hash_password = get_password_hash(body.password) 

    new_user = UserModel(
        name = body.name,
        username = body.username,
        hash_password = hash_password,
        email = body.email,
        role = body.role.value,
        department = body.department
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(body:LoginSchema,db:Session):
    user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Entered Wrong username")

    if not verify_password(body.password,user.hash_password):
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Entered Wrong password")

    exp_time = datetime.now() + timedelta(minutes= settings.EXP_TIME)    
    # exp_time = datetime.now() + timedelta(seconds=30)    

    token = jwt.encode({"_id":user.id, "exp":exp_time.timestamp()},settings.SECRET_KEY,settings.ALGORITHM)
    return {"access_token":token,"username":user.username,"name": user.name,"department": user.department,"role":user.role}

def is_authenticated(request:Request,db:Session):
    
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail = "You are unauthorized")

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = data.get("_id")
        

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail = "You are unauthorized")
        
        return user
    except InvalidTokenError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail = "You are unauthorized")
    
# --- Project Controller ---
# Note: We removed 'Depends' from here. It belongs in the Router.
def create_project(project_in: ProjectCreate, db: Session, current_user: UserModel):
    # CHECK 1: Is the user a manager?
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only managers can create projects."
        )

    # CHECK 2: Assign project to the Manager's department
    new_project = Project(
        name=project_in.name,
        description=project_in.description,
        department=current_user.department, 
        owner_id=current_user.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


# def get_user_projects(db: Session, user: UserModel):
#     # Option A: If you have a relationship set up in SQLAlchemy (e.g., user.projects)
#     # return user.projects 
    
#     # Option B: Standard Query (Safest approach)
#     projects = db.query(Project).filter(Project.owner_id == user.id).all()
#     return projects


def get_user_projects(db: Session, current_user: UserModel, name: str = None):
    """
    Fetch projects where the user is the OWNER -OR- has an ASSIGNED TASK.
    """
    query = db.query(Project)\
        .outerjoin(TaskModel, Project.id == TaskModel.project_id)\
        .filter(
            or_(
                Project.owner_id == current_user.id,        # Condition 1: User owns the project
                TaskModel.assigned_user_id == current_user.id   # Condition 2: User works in the project
            )
        )\
        .distinct() # IMPORTANT: Prevents duplicate projects if user has multiple tasks in one project

    # Optional: Filter by name if provided
    if name:
        query = query.filter(Project.name == name)

    return query.all()

def get_projects_by_name(db: Session, user: UserModel):
    # Option A: If you have a relationship set up in SQLAlchemy (e.g., user.projects)
    # return user.projects 
    
    # Option B: Standard Query (Safest approach)
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    return projects




def get_users_by_department(db: Session, current_user: UserModel) -> List[UserModel]:
    # 1. Check if the current user actually has a department assigned
    if not current_user.department:
        return [] 

    # 2. Query for all users with the matching department
    # You might want to exclude the current user from the list (.filter(UserModel.id != current_user.id))
    users = db.query(UserModel).filter(UserModel.department == current_user.department).all()
    
    return users



def delete_user(user_id: int, db: Session, current_user: UserModel):
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can delete users."
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")

    owns_project = db.query(Project).filter(Project.owner_id == user_id).first()
    assigned_task = db.query(TaskModel).filter(TaskModel.assigned_user_id == user_id).first()
    if owns_project or assigned_task:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete user with linked projects/tasks. Reassign or remove them first."
        )

    db.delete(user)
    db.commit()
    return Response(status_code=204)


def delete_project(project_id: int, db: Session, current_user: UserModel):
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can delete projects."
        )

    # 1. Find the Project
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete projects created by you."
        )

    # 2. DELETE ALL TASKS linked to this Project
    # We do this specifically to satisfy your requirement:
    # "if we delete project all the task inside that project also deleted"
    db.query(TaskModel).filter(TaskModel.project_id == project_id).delete()

    # 3. Delete the Project itself
    db.delete(project)
    
    # 4. Commit the changes
    db.commit()
    
    return Response(status_code=204)



def update_project(id: int, body: ProjectUpdateSchema, db: Session, current_user: UserModel):
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can update projects."
        )

    # 1. Find the Project
    project = db.query(Project).filter(Project.id == id).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {id} not found")

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update projects created by you."
        )

    # 2. Get Data (exclude_unset=True ignores fields you didn't send)
    data = body.model_dump(exclude_unset=True)

    # 3. Update Loop
    for key, value in data.items():
        setattr(project, key, value)
    
    # 4. Save
    db.commit()
    db.refresh(project)
    return project


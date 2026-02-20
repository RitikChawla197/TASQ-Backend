from fastapi import APIRouter, Depends, status,Request
from sqlalchemy.orm import Session
from typing import List
from src.users.dtos import UserSchema,UserResponseSchema,LoginSchema,ProjectResponse,ProjectCreate,ProjectUpdateSchema
from src.users.controller import register as register_user_controller,login_user,is_authenticated,create_project,get_current_user,get_user_projects,get_users_by_department,delete_project as delete_project_controller,update_project,delete_user as delete_user_controller
from src.utils.db import get_db
from src.users.models import UserModel

user_routes = APIRouter(prefix="/user")


@user_routes.post("/register",response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register_user(body: UserSchema, db: Session = Depends(get_db)):
    return register_user_controller(body, db)

@user_routes.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def signup_user(body: UserSchema, db: Session = Depends(get_db)):
    return register_user_controller(body, db)



@user_routes.post("/login", status_code=status.HTTP_200_OK)
def login(body:LoginSchema,db: Session = Depends(get_db)):
    return login_user(body,db)



@user_routes.get("/is_auth",response_model=UserResponseSchema,status_code=status.HTTP_200_OK)
def is_auth(request:Request,db: Session = Depends(get_db)):
    return is_authenticated(request,db)



# --- 2. The Logic Endpoint ---
@user_routes.post("/create_projects", response_model=ProjectResponse,status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    project_in: ProjectCreate, 
    db: Session = Depends(get_db), 
    # The Dependency is resolved HERE
    current_user: UserModel = Depends(get_current_user) 
):
    # We pass the resolved 'current_user' to the controller
    return create_project(project_in, db, current_user)



@user_routes.get("/projects", response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def get_all_projects(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Fetch all projects belonging to the currently logged-in user.
    """
    return get_user_projects(db, current_user)



@user_routes.get("/by_department", response_model=List[UserResponseSchema], status_code=status.HTTP_200_OK)
def get_department_colleagues(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Fetch all users who belong to the same department as the logged-in user.
    """
    return get_users_by_department(db, current_user)



@user_routes.delete("/project_delete/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # Optional: Ensure user is logged in
):
    """
    Delete a project and all its associated tasks.
    """
    # Optional: Check if the current_user actually owns this project before deleting
    # You can add logic here or in the controller to verify ownership.
    
    return delete_project_controller(project_id, db, current_user) 



@user_routes.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return delete_user_controller(user_id, db, current_user)


@user_routes.put("/update_project/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_project_endpoint(
    project_id: int, 
    body: ProjectUpdateSchema, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a project by its ID.
    Only fields sent in the body will be updated.
    """
    return update_project(project_id, body, db, current_user)
    






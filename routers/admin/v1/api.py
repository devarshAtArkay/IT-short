from datetime import date
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    Path,
    Query,
    Response,
    UploadFile,
    status
)
from sqlalchemy.orm import Session

import schemas
from dependencies import get_db

from routers.admin.v1.crud import system_user as system_users

router = APIRouter(
    prefix='/admin'
)

# Authentication
@router.post('/login', status_code=status.HTTP_200_OK, response_model=schemas.SystemUserLoginResponse, tags=['System User - Authentication'])
def sign_in(
    system_user: schemas.SystemUserLogin,
    db: Session = Depends(get_db)
):
    db_user = system_users.sign_in(db, system_user)
    return db_user


# A post request for creating a system_user
@router.post("/system_users",status_code=status.HTTP_201_CREATED ,tags=["System User"])
def create_system_user(system_user: schemas.SystemUserBase, db: Session = Depends(get_db)):

    return system_users.create_system_user(db=db, system_user=system_user)

#A get request to get all the user
@router.get(
    "/system_users/all", response_model=List[schemas.SystemUserSmall], tags=["System User"]
)
def get_all_system_users( token:str = Header(None),db: Session = Depends(get_db)):
    system_users.verify_token(db=db,token=token)
    all_system_users = system_users.get_all_system_users(db=db)
    return all_system_users


# A get request to get a system_user by an id
@router.get(
    "/system_users/{system_user_id}", response_model=schemas.SystemUserShow, tags=["System User"]
)
def get_system_user(
    system_user_id: str = Path(..., min_length=36, max_length=36),
    token:str = Header(None),
    db: Session = Depends(get_db),
):
    system_users.verify_token(db=db,token=token)
    db_system_user = system_users.get_system_user(db=db, system_user_id=system_user_id)

    return db_system_user


# A get request for getting the system_users with skip and limit,sortby,search,order
@router.get("/system_users", response_model=schemas.SystemUserList, tags=["System User"])
def get_student_list(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = Query(
        "all",
        min_length=3,
        max_length=10,
        description="sort by name, email, gender",
    ),
    order: str = Query(
        "all", min_length=3, max_length=4, description="Enter either asc or desc"
    ),
    search: str = Query(
        "all",
        min_length=1,
        max_length=50,
        description="Search by first_name,last_name,email",
    ),
    token:str = Header(None),
    db: Session = Depends(get_db),
):
    system_users.verify_token(db=db,token=token)
    all_system_users = system_users.get_system_user_list(
        db=db, skip=skip, limit=limit, sort_by=sort_by, order=order, search=search
    )
    return all_system_users

# put request to update system_user data
@router.put(
    "/system_users/{system_user_id}", response_model=schemas.SystemUserShow, tags=["System User"]
)
def update_system_user(
    system_user: schemas.SystemUserUpdate,
    token:str = Header(None),
    db: Session = Depends(get_db),
    system_user_id: str = Path(...,  min_length=36, max_length=36),
):
    system_users.verify_token(db=db,token=token)
    db_system_user = system_users.update_system_user(db=db, system_user_id=system_user_id, system_user=system_user)
    return db_system_user

#delete request to delete  system_user
@router.delete('/system_users/{system_user_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['System User'])
def delete_system_user(
    token: str = Header(None),
    system_user_id: str = Path(...,
                        min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    system_users.verify_token(db, token=token)

    system_users.delete_system_user(db, system_user_id=system_user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
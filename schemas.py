from pydantic import BaseModel, Field, validator
from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, status
from models import GenderEnum

from typing import List

#A base schema model for sytem_user
class SystemUserBase(BaseModel):

    first_name: str = Field(default=None, min_length=3, max_length=50)
    last_name: str = Field(default=None, min_length=3, max_length=50)
    email: str = Field(default=None, min_length=3, max_length=50)
    password: str = Field(min_length=3, max_length=50)
    phone_num: str = Field(min_length=10, max_length=15)
    gender: GenderEnum
    image: str
    image_type: str

    @validator('email')
    def valid_email(cls, email):
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

#A login schema for system user
class SystemUserLogin(BaseModel):
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=3, max_length=50)

#A response class for system user login
class SystemUserLoginResponse(BaseModel):
    id: str = Field(min_length=36, max_length=36)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=50)
    token: str

    class Config:
        orm_mode = True  

class SystemUserSmall(BaseModel):

    id:str
    name:str





# A schema which will be used to show students
class SystemUserShow(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone_num:str = None
    gender: GenderEnum
    image: str

    class Config:

        orm_mode = True
#A system user list schema
class SystemUserList(BaseModel):
    count:int
    list: List[SystemUserShow]

    class Config:
        orm_mode = True
#An update schema for update the system user
class SystemUserUpdate(BaseModel):

    first_name: str = Field(default=None, min_length=3, max_length=50)
    last_name: str = Field(default=None, min_length=3, max_length=50)
    email: str = Field(default=None, min_length=3, max_length=50)
    phone_num: str = Field(min_length=10, max_length=15)
    gender: GenderEnum
    image: str
    image_type: str

    @validator('email')
    def valid_email(cls, email):
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

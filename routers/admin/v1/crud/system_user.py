from datetime import datetime
from models import SystemUserModel
from fastapi import HTTPException, status
import schemas
from sqlalchemy.orm import Session
from sqlalchemy import or_
from libs.utils import generate_id, now, object_as_dict
import bcrypt
from jwcrypto import jwk, jwt
from config import config
import json
import traceback
from uuid import uuid4
import base64



# A create password function which encryptes a password and returns it
def _create_password(password):
    password = bytes(password, "utf-8")
    password = bcrypt.hashpw(password, config['salt'])
    password = password.decode("utf-8")
    return password


#A function to which creates user
def create_system_user(db: Session, system_user: schemas.SystemUserBase):

    if system_user.image != '':
        file_base64 = system_user.image
        file_base64 = file_base64.split(',')[1]
        file_64_decode = base64.b64decode(file_base64)
        extention = '.png' if system_user.image_type == 'image/png' else '.jpg'
        file_name = 'uploads/' + str(uuid4()) + extention
        with open(file_name, 'wb') as file:
            file.write(file_64_decode)
            file.close()

    system_user = system_user.dict()
    system_user_id = generate_id()

    password = system_user["password"]

    email = system_user['email']
    db_user = get_system_user_by_email(db, email=email)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='User already exist.')

    system_user["password"] = _create_password(password)
    

    # system_user["image"]
    del system_user['image_type']

    db_system_user = SystemUserModel(id=system_user_id,**system_user)
    db.add(db_system_user)
    db.commit()
    db.refresh(db_system_user)
    return db_system_user.id



#A function to get token
def get_token(user_id, email):
    claims = {
        'id': user_id,
        'email': email,
        'time': str(now())
    }

    # Create a signed token with the generated key
    key = jwk.JWK(**config['jwt_key'])
    Token = jwt.JWT(header={"alg": "HS256"}, claims=claims)
    Token.make_signed_token(key)

    # Further encrypt the token with the same key
    encrypted_token = jwt.JWT(
        header={'alg': 'A256KW', 'enc': 'A256CBC-HS512'}, claims=Token.serialize())
    encrypted_token.make_encrypted_token(key)
    token = encrypted_token.serialize()
    return token

#A function which verifies token
def verify_token(db: Session, token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing token')
    else:
        try:
            key = jwk.JWK(**config['jwt_key'])
            ET = jwt.JWT(key=key, jwt=token)
            ST = jwt.JWT(key=key, jwt=ET.claims)
            claims = ST.claims
            claims = json.loads(claims)
            db_user = get_system_user_by_email(db, email=claims['email'])
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        elif db_user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        return db_user


# A signin function which gets token and returns the loginschema
def sign_in(db: Session, system_user: schemas.SystemUserLogin):
    db_user = get_system_user_by_email(db, email=system_user.email)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    elif db_user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    hashed = db_user.password
    hashed = bytes(hashed, "utf-8")
    password = bytes(system_user.password, "utf-8")
    if not bcrypt.checkpw(password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
   
    db_user.token = get_token(db_user.id, db_user.email)
    return db_user


# function which gets system_user by id
def get_system_user_by_id(db: Session, system_user_id: str):

    db_system_user = (
        db.query(SystemUserModel)
        .filter(SystemUserModel.id == system_user_id, SystemUserModel.is_deleted == False)
        .first()
    )
    if db_system_user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No User available to show"
        )
    return db_system_user

def get_system_user(db:Session, system_user_id: str):

    db_system_user = get_system_user_by_id(db=db,system_user_id=system_user_id)
    return db_system_user

# A function to get system_user by email
def get_system_user_by_email(db: Session, email: str):
    return (
        db.query(SystemUserModel)
        .filter(SystemUserModel.email == email, SystemUserModel.is_deleted == False)
        .first()
    )

# gets all the system_users
def get_all_system_users(db: Session):

    rows = (
        db.query(SystemUserModel)
        .filter(SystemUserModel.is_deleted == False)
        .order_by(SystemUserModel.first_name, SystemUserModel.last_name)
        .all()
    )
    system_users = []
    for system_user in rows:
        name = system_user.first_name + ' ' + system_user.last_name
        _system_user = {
            'id': system_user.id,
            'name': name
        }
        system_users.append(_system_user)

    return system_users


# gets all the system_users with searching and sorting of first_name,last_name, gender 
def get_system_user_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = None,
    order: str = None,
    search: str = None,
):

    query = db.query(SystemUserModel).filter(SystemUserModel.is_deleted == False)

    if query is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Users available to show"
        )

    if search != "all":

        text = f"""%{search}%"""
        query = query.filter(
            or_(
                SystemUserModel.first_name.like(text),
                SystemUserModel.last_name.like(text),
                SystemUserModel.email.like(text),
                SystemUserModel.phone_num.like(text)
            )
        )

    if sort_by == "name":
        if order == "desc":
            query = query.order_by(SystemUserModel.first_name, SystemUserModel.last_name)
        else:
            query = query.order_by(SystemUserModel.first_name, SystemUserModel.last_name)
    elif sort_by == "email":
        if order == "desc":
            query = query.order_by(SystemUserModel.email.desc())
        else:
            query = query.order_by(SystemUserModel.email)
    elif sort_by == "gender":
        if order == "desc":
            query = query.order_by(
                SystemUserModel.gender.desc(),
                SystemUserModel.first_name.desc(),
                SystemUserModel.last_name.desc(),
            )
        else:
            query = query.order_by(
                SystemUserModel.gender, SystemUserModel.first_name, SystemUserModel.last_name
            )

    else:
        query = query.order_by(SystemUserModel.created_at.desc())

    rows = query.offset(skip).limit(limit).all()
    count = query.count()
    data = {"count": count, "list": rows}
    return data

#update the  system user

def update_system_user(db:Session,system_user_id:str,system_user: schemas.SystemUserUpdate):
    db_system_user = get_system_user_by_id(db=db, system_user_id= system_user_id)
    db_system_user.first_name = system_user.first_name
    db_system_user.last_name = system_user.last_name
    db_system_user.email = system_user.email
    db_system_user.gender = system_user.gender
    db_system_user.phone_num = system_user.phone_num
    db_system_user.updated_at = now()
    del system_user.image_type
    db.commit()
    db.refresh(db_system_user)
    return db_system_user

#delete function to delete the system user

def delete_system_user(db: Session, system_user_id: str):

    db_system_user = get_system_user_by_id(db=db, system_user_id=system_user_id)
    db_system_user.is_deleted = True
    db_system_user.updated_at = now()
    db.commit()
    return
import logging
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from typing import Annotated
from sqlmodel import Session
from todo_app.auth import get_db_user , hashPassword, validate_user
from todo_app.db import get_session
from todo_app.model import User, register_User


user_router = APIRouter(prefix="/user",
                         tags=["user"] ,
                          responses={404: {"description": "Not found"}})
@user_router.get("/")
async def get_user():
    return {"message": "Hello User"}
#new_user:Annotated[register_User, Depends()]
@user_router.post("/register")
async def register_user(username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()] , session : Annotated[Session , Depends(get_session)] ,request : Request):
    
    db_user = get_db_user(session , username , email)
    if db_user:
        raise HTTPException(status_code=409 , detail="User already exists")
    hashed_pwd = hashPassword(password)    
    user = User(username = username , email = email , password = hashed_pwd) 
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f"""Welcome to Tick Task {user.username}  """}   
@user_router.get('/me')
async def user_profile (current_user:Annotated[User, Depends(validate_user)]):

    return current_user
@user_router.post('/testme')
async def testRoute(user : register_User):
    return user
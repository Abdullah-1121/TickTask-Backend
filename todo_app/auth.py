from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlmodel import select
from jose import jwt , JWTError
from todo_app.db import get_session
from todo_app.model import RefTokenModel, TokenModel, User
from todo_app.settings import SECRET_KEY


ALGORITHYM = 'HS256'
EXPIRY_TIME = 60
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pswrd_context = CryptContext(schemes=["bcrypt"])
def hashPassword(password : str):
    return pswrd_context.hash(password)

# Verify Password functionality
def verify_password(password , hashedPassword):
    return pswrd_context.verify(password,hashedPassword)
# Method to get the existing user
def get_db_user(session:Annotated[Session , Depends(get_session)] , username : str | None = None , email : str | None = None):
    # writing statement to query the database
    statement  = select(User).where(User.username == username )
    user = session.exec(statement).first()
    if not user :
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user :
            return user
    return user 
   
# Login user or Authenticate user functionality
def login_user (username , password , session : Annotated[Session , Depends(get_session)]):
    db_user = get_db_user(session=session , username=username)
    if not db_user:
        return False
    if not  verify_password(password=password , hashedPassword= db_user.password):
        return False
    return db_user

# Creating Access token functionality
def create_token (data: dict , expiry_time:timedelta|None):
    data_to_encde = data.copy()
    if expiry_time : 
        expire = datetime.now(timezone.utc) + expiry_time
    else :
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)   

    data_to_encde.update({"exp": expire})
    encoded_jwt = jwt.encode(
        data_to_encde, SECRET_KEY, algorithm=ALGORITHYM, )
    return encoded_jwt

# Validating the user through the access token 
def validate_user(token : Annotated[str , Depends(oauth_scheme)] , session : Annotated[Session , Depends(get_session)]):
    credential_exception = HTTPException(
        status_code=401 ,
        detail='Invalid token , Please login Again',
        headers={"www-Authenticate":"Bearer"}
    )
   
    try:
        # Fixing the typo in ALGORITHYM and algorithms
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHYM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenModel(username=username)
    except JWTError:
        raise credential_exception
    
    db_user = get_db_user(session, username=token_data.username)
    
    # Fixing the logic here: raise the exception if the user does not exist
    if db_user is None:
        raise credential_exception

    return db_user

# create refresh token functionality
def  create_refresh_token(data: dict , expiry_time:timedelta|None):
    data_to_encde = data.copy()
    if expiry_time : 
        expire = datetime.now(timezone.utc) + expiry_time
    else :
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)   

    data_to_encde.update({"exp": expire})
    encoded_jwt = jwt.encode(
        data_to_encde, SECRET_KEY, algorithm=ALGORITHYM, )
    return encoded_jwt
# validate refresh token functionality
def validate_refresh_token(token : str , session : Annotated[Session , Depends(get_session)]):
    credential_exception = HTTPException(
        status_code=401 ,
        detail='Invalid token , Please login Again',
        headers={"www-Authenticate":"Bearer"}
    )
   
    try:
        # Fixing the typo in ALGORITHYM and algorithms
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHYM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credential_exception
        token_data = RefTokenModel(email=email)
    except JWTError:
        raise credential_exception
    
    db_user = get_db_user(session, email=token_data.email)
    
    # Fixing the logic here: raise the exception if the user does not exist
    if db_user is None:
        raise credential_exception

    return db_user
    

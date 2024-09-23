from fastapi import Form
from pydantic import BaseModel
from sqlmodel import SQLModel, Field ,Session , create_engine
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated



#Create Model 
# There are two types of Model , Data Model (validates data) , Table Model (creates a table in the database)
#SQL Model has the capability that we can create a single model that can validates data as well as creates a table
class Todo(SQLModel , table=True):
    #id is created by db itself , user will not set it that's why it will also be null and act as a Primary Key
    id:int | None = Field(default=None,primary_key=True)
    content:str = Field(index=True,min_length=3,max_length=54)
    is_completed : bool = Field(default=False)
    user_id : int = Field(foreign_key="user.id")

# Model for User 
class User (SQLModel , table=True):
    id:int = Field(default=None,primary_key=True)
    username : str 
    email : str 
    password : str

class New_Todo(BaseModel):
    
    content:str = Field(index=True,min_length=3,max_length=54)
    

class register_User(BaseModel):
    username : Annotated[str , Form() ]
    email : Annotated[str , Form() ] 
    password : Annotated[str , Form() ]
    #  username:Annotated[ str , Form()] 
    #  email: Annotated[ str , Form()] 
    #  password: Annotated[ str , Form()] 
      
class token(BaseModel):
    access_token : str 
    token_type : str
    refresh_token : str | None 
class TokenModel(BaseModel):
    username : str
class Todo_Edit(BaseModel):
    content:str 
    is_completed:bool
class RefTokenModel(BaseModel):
    email : str     

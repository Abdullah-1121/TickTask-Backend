from datetime import timedelta
from fastapi import FastAPI , Depends , HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field , create_engine , Session , select
from todo_app import settings
from typing import Annotated
from contextlib import asynccontextmanager
from todo_app.auth import EXPIRY_TIME, create_refresh_token, create_token, login_user, validate_refresh_token, validate_user
from todo_app.db import create_Tables , get_session 
from todo_app.model import New_Todo, Todo, Todo_Edit, User, token
from todo_app.router import user
from fastapi.middleware.cors import CORSMiddleware



   
# dummy data 
# todo1 : todo = todo(content = 'first task')
# todo2: todo = todo(content = 'secondTask')
# # we will create separate sessions for each functionality or a transaction
# session = Session(engine)
# session.add(todo1)
# session.add(todo2)
# print(f'Before commit {todo1}')
# session.commit()
# print(f'after commit {todo1}')
# session.close()




#context manager creates a context for our app , it will define the functions that will perform when our app will run  
@asynccontextmanager
async def lifespan (app:FastAPI):
    print('creating tables')
    create_Tables()
    print('Tables created')
    yield




app = FastAPI(lifespan=lifespan ,title = 'Todo-App' , version = "1.0.0")
app.include_router(router = user.user_router)
@app.get("/")
def root ():
    return {"message": "Welcome to Todo App"}
  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Login Route 
expiry = timedelta( minutes=EXPIRY_TIME)
@app.post("/token" , response_model=token)
async def login(form_data : Annotated[OAuth2PasswordRequestForm , Depends()] , session : Annotated[Session , Depends(get_session)]):
   print(form_data.username)
   user =  login_user(username=form_data.username , password=form_data.password , session=session)
   if not user:
       raise HTTPException(status_code=409 , detail="Invalid Email or Username")
   access_token = create_token({"sub":form_data.username }, expiry_time=expiry)
   refresh_expiry = timedelta(days=7)
   refresh_token = create_refresh_token({"sub":user.email }, expiry_time=refresh_expiry)
   return token( access_token = access_token ,  token_type='bearer' , refresh_token = refresh_token )


@app.get("/token/refresh")
async def getRefreshToken(oldToken:str , session : Annotated[Session , Depends(get_session)]):
    credential_exception = HTTPException(
        status_code=401 ,
        detail='Invalid token , Please login Again',
        headers={"www-Authenticate":"Bearer"}
    )
    user = validate_refresh_token(oldToken , session)
    if not user : 
        raise credential_exception
    refresh_expiry = timedelta(days=7)
    access_token = create_token({"sub":user.username }, expiry_time=expiry)
    refresh_token = create_refresh_token({"sub":user.email }, expiry_time=refresh_expiry)
    return token( access_token = access_token ,  token_type='bearer' , refresh_token = refresh_token )
    

@app.post("/todos" , response_model=Todo)
def createTodo(current_user: Annotated[User , Depends(validate_user)], todo:New_Todo , session :Annotated[Session , Depends(get_session)] ):
    new_todo = Todo(content =todo.content , user_id=current_user.id )
    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)
    return new_todo

@app.get("/todos" , response_model=list[Todo])
def getAllTodos(current_user: Annotated[User , Depends(validate_user)],session :Annotated[Session , Depends(get_session)]):
    todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
     
    return todos

@app.get("/todos/{id}" , response_model=Todo)
def getSingleTodo(id: int, current_user: Annotated[User , Depends(validate_user)], session: Annotated[Session, Depends(get_session)]):
    current_user_todo = session.exec(select(Todo).where(Todo.user_id == current_user.id))
    single_todo = next((todo for todo in current_user_todo  if todo.id == id),None)
    if single_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return single_todo
    
    
    

@app.put("/todos/{id}")
def editTodo(id:int , todo:Todo_Edit ,current_user: Annotated[User , Depends(validate_user)], session :Annotated[Session , Depends(get_session)]):
    current_user_todo = session.exec(select(Todo).where(Todo.user_id == current_user.id))
    single_todo = next((todo for todo in current_user_todo  if todo.id == id),None)
    if single_todo:
        single_todo.content = todo.content
        single_todo.is_completed = todo.is_completed
        session.add(single_todo)
        session.commit()
        session.refresh(single_todo)
        return single_todo
    else :
        raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{id}")
def deleteTodo(id: int, current_user: Annotated[User , Depends(validate_user)],  session: Annotated[Session, Depends(get_session)]):
     current_user_todo = session.exec(select(Todo).where(Todo.user_id == current_user.id))
     single_todo = next((todo for todo in current_user_todo  if todo.id == id),None)
     if single_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
     session.delete(single_todo)
     session.commit()
     return {"message": "Todo deleted"}    
    
# Step-1: Create Database on Neon
# Step-2: Create .env file for environment variables
# Step-3: Create setting.py file for encrypting DatabaseURL
# Step-4: Create a Model
# Step-5: Create Engine
# Step-6: Create function for table creation
# Step-7: Create function for session management
# Step-8: Create contex manager for app lifespan
# Step-9: Create all endpoints of todo app
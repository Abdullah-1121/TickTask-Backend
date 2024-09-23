from fastapi.testclient import TestClient
from fastapi import FastAPI , dependencies 
from todo_app import settings
from sqlmodel import SQLModel , create_engine , Session
from todo_app.main import app , get_session
import pytest

connection_string : str = str(settings.TEST_DB_URL).replace("postgresql","postgresql+psycopg")
engine = create_engine(connection_string , connect_args= {"sslmode":"require"} ,pool_recycle=300  ) 
#========================================================================================
# Refactor with pytest fixture
# 1- Arrange, 2-Act, 3-Assert 4- Cleanup

@pytest.fixture(scope="module", autouse=True)
def get_db_session():
    SQLModel.metadata.create_all(engine)
    yield Session(engine)

@pytest.fixture(scope='function')
def test_app(get_db_session):
    def test_session():
        yield get_db_session
    app.dependency_overrides[get_session] = test_session
    with TestClient(app=app) as client:
        yield client

#=========================================================================================
# Test 1 of Root 
def test_root():
    client = TestClient(app=app)
    response = client.get('/')
    data = response.json()
    #checking if the test response matches our actual response
    assert response.status_code == 200
    assert data == {"message": "Welcome to Todo App"}
#Test 2 of Create Todo Functionality
def test_createTodo(test_app):

#As we know we have to create session to perform the functionalities , but Now we are in testing phase , if we use the get
# method from the main file that is connected with main branch of our code , there will be inconsistency , so we have to 
#overWrite this session with our test session that will be using the test branch of our db
    #Creating tables
    # SQLModel.metadata.create_all(engine)   
    # with Session(engine) as session :
    #     def db_session_overwrite():
    #         return session
    #     app.dependency_overrides[get_session] = db_session_overwrite
    #     client = TestClient(app=app)
        test_todo= {"content":"create a test todo list"}
        response = test_app.post('/todos/' , json = test_todo)
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == test_todo["content"]
        

#Test 3 
def test_getAllTodos(test_app):
    # SQLModel.metadata.create_all(engine)   
    # with Session(engine) as session :
    #     def db_session_overwrite():
    #         return session
    #     app.dependency_overrides[get_session] = db_session_overwrite
    #     client = TestClient(app=app)
        response = test_app.get('/todos')
        assert response.status_code == 200

#Test 4 Get a single todo
def test_getSingleTodo(test_app):
    # SQLModel.metadata.create_all(engine)   
    # with Session(engine) as session :
    #     def db_session_overwrite():
    #         return session
    #     app.dependency_overrides[get_session] = db_session_overwrite
    #     client = TestClient(app=app)
        test_todo = {'content':"test todo for getsingle"}
        response = test_app.post('/todos',json=test_todo)
        todo_id = response.json()["id"]
        res = test_app.get(f'todos/{todo_id}')
        data=res.json()
        assert res.status_code == 200
        assert data["content"] == test_todo["content"]

#Test 5 - Edit todo
def test_editTodo(test_app):
    #   SQLModel.metadata.create_all(engine)   
    #   with Session(engine) as session :
    #     def db_session_overwrite():
    #         return session
    #     app.dependency_overrides[get_session] = db_session_overwrite
    #     client = TestClient(app=app)
        test_todo = {"content":"edit todo test", "is_completed":False}
        response = test_app.post('/todos/',json=test_todo)
        todo_id = response.json()["id"]
     
        edited_todo = {"content":"We have edited this", "is_completed":False}
        response = test_app.put(f'/todos/{todo_id}',json=edited_todo)
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == edited_todo["content"]
        
def test_deleteTodo(test_app):
        # SQLModel.metadata.create_all(engine)   
        # with Session(engine) as session :
        #  def db_session_overwrite():
        #     return session
        # app.dependency_overrides[get_session] = db_session_overwrite
        # client = TestClient(app=app)
        test_todo = {"content":"edit todo test", "is_completed":False}
        response = test_app.post('/todos/',json=test_todo)
        todo_id = response.json()["id"]
        res = test_app.delete(f'/todos/{todo_id}')
        data = res.json()
        assert res.status_code == 200
        assert data["message"] == "Todo deleted"


        

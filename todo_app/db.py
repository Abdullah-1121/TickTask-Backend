from sqlmodel import SQLModel, Field ,Session , create_engine
from todo_app import settings

#SSl mode = required will encrypt our communication
#echo = true , shows all the work done by the engine on the terminal
#Engine is one for whole application
connection_string : str = str(settings.DB_URL).replace("postgresql","postgresql+psycopg")
engine = create_engine(connection_string , connect_args= {"sslmode":"require"} ,pool_recycle=300  )  
def create_Tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
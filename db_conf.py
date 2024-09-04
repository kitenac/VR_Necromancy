'''
Configuring access to Database
- engine (creds + database type)
- individual db-session for each request
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base # all Tables from models inherits from it => can create `em here 


# accessing DATABASE, TODO: export some params to .ENV:

# TODO: get this parametr as arg for module VR_Necromancy.main (requires creating separate function to create engine by given param and refactoring all files that uses engine)
WORK_MODE = 'dev'  # dev - for development, prod - for creating image 

# dev/prod hosts ips
hosts = {
    'dev': '127.0.0.1',        # for development
    'prod': 'MySQL_Pet_PROD'   # when backend run as container | note: Docker`s internal DNS would resolve container`s ip by name of container
}

host, port = hosts[WORK_MODE], '3306'
sql_vers, driver = 'mysql', 'pymysql'      
usr, pwd = 'root', 'root'
db_name = 'VR_Pharmacy_v2'


DATABSE_URL = f"{sql_vers}+{driver}://{usr}:{pwd}@{host}:{port}/{db_name}"
engine = create_engine(DATABSE_URL)

# Создаём все таблицы, если ещё не были созданы
Base.metadata.create_all(engine)

# object to create new sessions
sessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine) 


def get_db_session():
    '''
        access to db,
        auto-handle db session - close when session is unused  ('finaly' block)
    '''

    db = sessionFactory() # create session with db
    try:
        yield db
    finally:
        db.close()        # auto-closing session when yielded above session(db) is abandoned (function that used session is completed => controll return in get_db and 'finally' closes session)



# TODO - как правило сессия удобней, но бывает и подключение нужно иногда 
def create_connection():
    pass



if __name__ == '__main__':
    '''
    Как использовать БД:
    '''
    
    SessionLocal = get_db_session()

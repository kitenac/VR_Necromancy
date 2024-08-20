'''
Configuring access to Database
- engine (creds + database type)
- individual db-session for each request
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession # async versions
from models import Base # all Tables from models inherits from it => can create `em here 


# accessing DATABASE, TODO: export some params to .ENV:
host, port = '127.0.0.1', '3306'
sql_vers, driver = 'mysql',  'asyncmy' # and for sync mode - 'pymysql'      
usr, pwd = 'root', 'root'
db_name = 'VR_Pharmacy_v2'


DATABSE_URL = f"{sql_vers}+{driver}://{usr}:{pwd}@{host}:{port}/{db_name}"
engine = create_async_engine(DATABSE_URL)

async def init_db():
    '''
    Создать все таблицы, если ещё не были созданы
    '''
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        

# object to create new sessions
sessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False)  # async vers

async def get_db_session() -> AsyncSession:
    '''
        access to db,
        auto-handle db session - close when session is unused (yield gives generator - which is single-use and`ll closed after use) 
    '''
    async with sessionFactory() as db:
        yield db  # yield - not return for Session - generator => session will be lost after using




# TODO - как правило сессия удобней, но бывает и подключение нужно иногда 
async def create_connection():
    pass



if __name__ == '__main__':
    '''
    Как использовать БД:
    '''
    
    SessionLocal = get_db_session()

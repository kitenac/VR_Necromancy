'''
 - Server configuration 
 - HTTP-app functions:
   - HTTP methods for different resources 
   - HTTP parametrs extraction (body, query, Referer, path-params)
   - handling HTTP exceptions
   - TODO: preserving HTTP response here (default status_code must be here for each method: like in DELETE methods)
      - FIX: /search methods gets already formed API_Response => must inject status code

   
CRUD: Core for vr_app`s HTTP methods` handlers
'''
from fastapi import FastAPI, HTTPException, Body, Query, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

import logging 
from typing import Optional, List 

import schemas # data schemas
import CRUD # http methods` handlers
from db_conf import get_db_session


# ==== HTTP App configuration
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(''.join(open('README.md', 'r').readlines())) # display README.md in logs on start

# App settings
API_BASE = '/api/v1.0'
vr_app = FastAPI(root_path=API_BASE, title='VR_Necromancy')

# CORS - настройка разрешённых ресурсов сервера
CORS_conf = {
  'origins': ['http://localhost:1337'],  #  адреса 
  'allow_creds': True,   # Разрешить отправку учётных данных
  'methods': ["*"],   # GET, POST, ...
  'headers': ["*"]    # Accept, Content-Type, Referer, Content-Length ...
}

# Добавим middleware для CORS
vr_app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_conf['origins'],     
    allow_credentials=CORS_conf['allow_creds'],   
    allow_methods=CORS_conf['methods'],     
    allow_headers=CORS_conf['headers'],     
    
)



# ====  HTTPException handling

''' [Explain of decorator logic]

Объяснение декораторов в фреймворках - откуда там параметры 
- коротко: мы всё также вызываем функцию(функцию-генератор), только теперь это функция, сгенерированная функцией от параметров 

Код:
  vr_app = FastAPI()

  @vr_app.post('/groups/search', summary='View groups')
  def my_fun(...)
	  pass

благодаря my_fun() ты определяешь, как будет себя вести POST функция, сгенерированная вызовом метода .post приложения vr_app (объекта FastApi):
vr_app.post('/groups/search', summary='View groups')
- т.е. метод post в FastApi - генератор функций POST
'''

# TODO: upgrade, mb
@vr_app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, e: HTTPException):
    return JSONResponse(
        status_code=e.status_code,
        
        content=schemas.API_Response(
          code=e.status_code,
          status=e.detail
        ).model_dump()
    )




# ==== Search: pagination + filtering + sorting
@vr_app.post('/groups/search', summary='View groups')
async def groups_search(
    request: Request,  # client_url - fastapi handles
    filter: Optional[List[schemas.RequestBody.FilterItem]] = None,  # Body parameter
    with_aliased: Optional[schemas.RequestBody.With] = Body(default=None, alias="with"),  # Use Body to extract 'with' directly
    limit: int = 10,
    page: int = 1,
    order: list[str] = Query(['id'], alias='order[]'),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
  ):
    '''                       (Docs)
      Get all groups
      - TODO: pagination
    '''
    
    params = schemas.RequestQuery(limit=limit, page=page, order=order)
    return await CRUD.search_groups(SessionLocal, params=params, filter=filter)
        
 

@vr_app.post('/students/search', summary='View students of group')
async def students_search(
    request: Request,  # client_url can be retrived from Header "Referer"
    filter: Optional[List[schemas.RequestBody.FilterItem]] = None,  # Body parameter
    with_aliased: Optional[schemas.RequestBody.With] = Body(default=None, alias="with"),  # Use Body to extract 'with' directly
    limit: int = 10,
    page: int = 1,
    order: list[str] = Query(['id'], alias='order[]'),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Get all students of chosen group,
      pagination, filtering
    '''
    
    client_url = request.headers.get('referer') #  from Header "Referer"
    group_id = client_url.split('/')[-1] # last arg of client`s url is group id
    params = schemas.RequestQuery(limit=limit, page=page, order=order)
    
    return await CRUD.search_students(SessionLocal, params=params, filter=filter, group_id=group_id)
     

# ==== Create
@vr_app.post('/groups', summary='Add group')
async def students_create(
    name: str = Body(),
    email: str = Body(),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Create a new group 
    '''
    group = schemas.Group(name=name, email=email)
    return await CRUD.create_group(db=SessionLocal, group=group)

@vr_app.post('/students', summary='Add student')
async def students_create(
    full_name: str = Body(),
    group_id: str = Body(),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Create new student 
    '''
    student = schemas.Student(group_id=group_id, full_name=full_name)
    return await CRUD.create_student(db=SessionLocal, student=student)

# ==== Delete. 
# errors here goes to HTTPExeption and handler in at very start of main.py 
@vr_app.delete('/groups/{id}', status_code=200, summary='Delete group by id')
async def group_delete(
    id: str,
    SessionLocal: Session = Depends(get_db_session),
    response = Response() # response object of fastapi: headers, status_code and other crusual lays here
):
    '''                   (Docs)
    Delete selected group 
    '''
    status = await CRUD.delete_group(db=SessionLocal, id=id)
    
    return schemas.API_Response(
        status=status,
        code=response.status_code
    )


@vr_app.delete('/students/{id}', status_code=200, summary='Delete student by id')
async def student_delete(
    id: str,
    SessionLocal: Session = Depends(get_db_session),
    response = Response() # response object of fastapi: headers, status_code and other crusual lays here
):
    '''                   (Docs)
    Delete selected student 
    '''
    status = await CRUD.delete_student(db=SessionLocal, id=id)
    
    return schemas.API_Response(
        status=status,
        code=response.status_code
    )


# ==== Redo
@vr_app.put('/groups/{id}', status_code=200, summary='redo group')
async def group_redo(
  id: str,
  redo_group: schemas.PUT_Group,
  SessionLocal: Session = Depends(get_db_session),
  response = Response()
):
    '''
    Redo selected group by email/name/both
    '''

    if not redo_group.name and not redo_group.email:
        raise HTTPException(status_code=400, detail='Bad request: either name or email must be specified')

    await CRUD.redo_group(db=SessionLocal, id=id, redacted_group=redo_group)
    return schemas.API_Response(
        status='Successfully redacted group',
        code=response.status_code
    )

@vr_app.put('/students/{id}', status_code=200, summary='redo student')
async def group_redo(
  id: str,
  redo_student: schemas.PUT_Student,
  SessionLocal: Session = Depends(get_db_session),
  response = Response()
):
    '''
    Redo selected student by fullname
    '''

    if not redo_student.full_name:
        raise HTTPException(status_code=400, detail='Bad request: full_name must be specified')

    await CRUD.redo_student(db=SessionLocal, id=id, redacted_student=redo_student)
    return schemas.API_Response(
        status='Successfully redacted student',
        code=response.status_code
    )

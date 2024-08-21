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


'''
План:
 I. Учимся какать
    
    1) + Описание данных и связь с БД: models + schemas  

    1.1) + Поиграться с ORM: 
          + Создание таблиц из ORM
          + создание запроса, 
          + пагинация
          + оптимизация запросов

    1.2) + Разобраться с отловом query, body параметров

    2) + создание/удаление/поддержка session  
  
  2.1)+ group_id - научиться доставать из url клиента (Header: Referer)
    - поменял в браузере дефолтную Refferr-Policy - больше обрезки url клиента нет!
  2.2) + БД - при запуске просит крипту, если из кода первый раз подключаться, а не из SQL Workbench
 
  + redirect 307 убрать - все запросы дублируются
  + почему-то фильтр desc full_name работает криво 
  + пагинация и создание работают отлично

  + [Ачивка] Удаление сущности с констрейнтом (ограничением)
      - когда группы удаляшь - нужно сначала её студентов удалить, т.к. они ссылаются на её group_id
      - там ещё интересный случай, с тем, что не всегда 404 нужно возвращать если ничего не нашлось (в пустой группе запрос на удаление будет из пустого списка, НО это не значит, что ничего не нашлось по выбранному id - просто ничего не нужно ужалять)

  +  Delete, Update добавть      

  >>>> CURRENT >>>>  
 
   Router добавить и тогда main можно разнести красиво
        - 26:40 - https://www.youtube.com/watch?v=gBfkX9H3szQ&list=PLeLN0qH0-mCVQKZ8-W1LhxDcVlWtTALCS
 
    Даты в БД есть, но они почему-то не доходят
   >>> Узнать, как это исправить/жить с этим - мб загуглить pydentic + autogenerating fields

    - а ещё начал async ветку - асинхронное обращение к бд

  >>> Разобраться, как работает автозакрытие сессий и Depends:
  -  получается, что finally отрабатывает только после завершения search()
        >>> Есть ответ в Obsidian Fastapi/problem_session - на примере сравнения с Depends()

  >>> CRUDб main раздуло слишком - создай папку отдельную и по разным файлам разбей, а CRUD.py - их агрегатором пусть будет 
  >>> БД - students_count автоматически считать мб можно - COUNT (STUDENTS: id == id)
      - это называется триггер) - есть смысл для надёжности использовать его
      - как вариант в models: (default = func.count(...))

  >>>> CURRENT >>>> 

  
  3) Должок по теории закрыть: 
      Про концепцию ORM посомтреть (как в память идёт отображение таблиц - маппинг таблицы и объекта, какой жизненый цикл в памяти у объекта, связанного с таблицей(моделью таблицы))  
      Посмотреть ОБЗОРНО туторы по FastAPI, sqlalchemy
      - расширить кругозор - без конспектов - на понимание
     
   

  II. Как разбирусь и создам сессии:
  Буду общаться с БД - данные на сайте будут от туда

  *) перенимать хорошие практики из реальных fastapi проектов - тут хорошо читается:
     https://github.com/nsidnev/fastapi-realworld-example-app/blob/master/app/api/dependencies/database.py

  1) CRUD - первый эндпоинт 
  
  2) коды состояний возвращать и статус
    - CRUD.delete + @vr_app.delete('/groups/{id}', status_code=204)
      - уже в таком ключе писал 

    - коды состояний всякие бывают - почитать/видос, 
         204 - No Content - OK и доп. инфа не требуется для ответа (успешное удаление, например)
         400 - Bad Request

    >> Это уже шаг к RESTful principles 
       and provides clear feedback to the client regarding the outcome of their request
  
  3) + пагинация
  4) CRUD по всем страницам
    - вот тут /quests дадут мне просраться))) - но там только R - Read
  5) валидировать ввод форм при создании/редактировании, а ещё поиск - чтоб SQL-инъекций не было  
    - email валидировать точно: not null (by model) + regexp
    - full_name для студентов - чтоб 3 слова было в строке

  *) мб тестами покрыть методы - pytest и логгирование добавить - sentry (5 строк кода и на их фронте есть всевозможная аналитика с дашбордами)
  *) рефакторинг 
    - разбить schemas, 
    
    >>> определиться с ролью методов обработки путей в main и CRUD - кто за что отвечает, а то сейчас main - только отлавливает запросы, а CRUD всё делает, даже данные ответа (там по логике чище показалось реализовать)
        - в шапке на английском расписал, за что должен main отвечать
    
    - читаемость повысить, добавить ООП-патернов
  **) что-то со скоростью создания сделать - ооочень долго идёт, мб с сессиями что или сервер с uvicorn сменить, мб параметры сервера покрутить - ресурсов юольше дать
    
  1000) !!! Dockerfile приложения написать и закинуть Image на DockerHub 
        + DockerCompose - чтоб БД тоже была
  *) есть бесплатные хостинги - можно туда залить
  
  III. Когда всё готово  
  Приложение функционирует, как раньше, всё круто,НО, 
  надо его облагородить:
    0) Redis подключить, в Fastapi достаточно декоратор будет навесить функциям: 6:20
        https://www.youtube.com/watch?v=Kr-V4IgJFes
    1) разделить приложение на два микросервиса (две отдельные кодовые бызы)
       как вариант на:
       - квесты 
       -группы
      + ещё фронт в отдельном контейнере
    
    * попробовать один из микросервисов на SOAP/GRPC сделать

    2) связать их по HTTP
    3) а теперь связать их через Kafka
    
    **) Пополнение Зоопарка:
        celery - для управления асинхронными запросами (нагрузку можно эмииовать)
         - для create методов пригодится - см. TODO в crud/create()
        много других классных идей со ссылками:
        https://www.youtube.com/watch?v=Kr-V4IgJFes
        - Logging 
    ***) Добавить бинарных файлов 
        - отдельный микросервис под работу с бинарями
          * на GRPC/SOAP сделать
        - отдельный фронт на Django под картинки/видео (уже готовый взять)
        - для хранения бинарных файлов другую СУБД использовать
        - не обязательно со старым фронтом связывать - достаточно, что по данным есть связь, но мб новый фронт будет ссылаться на старый
        

    1000) !!! Dockerfile & Dockercompose написать и закинуть Image на DockerHub 
'''

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
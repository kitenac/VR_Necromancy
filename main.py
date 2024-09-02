'''

Project structure:

0) main - HTTP-App configuration 

1) routers (~mini-apps):
 - HTTP-app functions (parted into routerers from .routers):
   - HTTP methods for different resources 
   - HTTP parametrs extraction (body, query, Referer, path-params)
   - handling HTTP exceptionsgit 
   
2) CRUD: 
  - Core for each vr_app`s router HTTP methods` handlers

3) models - ORM

4) schemas - data schema defenitions + auto validation - thanks to pydentic

Additional apps:
 1) admin_page - CRUD through external entities

'''
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

import logging 
from . import schemas # data schemas
from .routers import groups, students, quests, progress, external # like mini-apps  
from .admin_page import create_admin_page


# ==== HTTP App configuration
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(''.join(open('VR_Necromancy/README.md', 'r').readlines())) # display README.md in logs on start (added vr_app/ - due context shifted to parent directory - due we use module)

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



# Mount the admin page app to main app
admin = create_admin_page(vr_app)
vr_app.mount(app=admin, path='/admin')

# URL prefixes handlers 
# - like mini-apps for each url-prefix  (to manage app here we use @vr_app, inside routers - @router)
vr_app.include_router(groups.router)    # for /groups*
vr_app.include_router(students.router)  # for /students*
vr_app.include_router(quests.router)    # for /quests*
vr_app.include_router(progress.router)  # for /progress*

# mocking endpoint [not needed anymore due we already have admin_page] - for data that must go from differenr service
vr_app.include_router(external.router)  # for /external*

# Добавим middleware для CORS
vr_app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_conf['origins'],     
    allow_credentials=CORS_conf['allow_creds'],   
    allow_methods=CORS_conf['methods'],     
    allow_headers=CORS_conf['headers'],     
    
)

# ====  HTTPException handling
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



if __name__ == "__main__":
    uvicorn.run(vr_app, host="0.0.0.0", port=8001)

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

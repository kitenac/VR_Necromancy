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
  + пагинация 

  + [Ачивка] Удаление сущности с констрейнтом (ограничением)
      - когда группы удаляшь - нужно сначала её студентов удалить, т.к. они ссылаются на её group_id
      - там ещё интересный случай, с тем, что не всегда 404 нужно возвращать если ничего не нашлось (в пустой группе запрос на удаление будет из пустого списка, НО это не значит, что ничего не нашлось по выбранному id - просто ничего не нужно ужалять)

  +  Delete, Update добавть      

  + Router добавить и тогда main можно разнести красиво

   + реализовать добавление квестов (через доку дёргать) и добиться, чтоб группы отображалиь в странице заданий   
   + Даты в БД - починил

    - а ещё начал async ветку - асинхронное обращение к бд

   + main раздуый разнёс 
   + CRUD - тоже в модуль оформить
   
   + админку добавил - для удобной работы с Task/Quest
   + CRUD по всем страницам
  
  >>>> CURRENT >>>>  

  >>> QuestPage:
  
    УРА - уже отображается прогресс!!!!
    + пофиксил join в progress

    + cascade-ом порешать удаление всех дочерних сущностей при удалении родителькой
        [+] на удалении студентов работает - сессии квестов с тасками удалятся
        [+] при удалении групп студенты, а вместе с ними и сессионные квесты и таски удаляются


    И всё, только
      + Dockerfile приложения написать и закинуть Image на DockerHub 
        + DockerCompose - чтоб БД тоже была
      + залить на гитхаб  

    Потом - по 30 минут/день в перерывах от диплома
      - моменты из теории смотреть потихоньку 


  >>>> CURRENT >>>> 

  
  3) Должок по теории закрыть/кругозор: 
      1) Про концепцию ORM посомтреть (как в память идёт отображение таблиц - маппинг таблицы и объекта, какой жизненый цикл в памяти у объекта, связанного с таблицей(моделью таблицы))  
      
      2) Посмотреть ОБЗОРНО туторы по FastAPI, sqlalchemy
      - расширить кругозор - без конспектов - на понимание
        
        - relationship - очень интересно, что из себя представляет/как работает - т.к. он помог в адимнке внешние ключи задать
            - при этом поля с relationship в реальной таблице нет (проверял) - это как-бы загатовка под запрос к БД - таблицы выбраной
        - cascade парметр в relationship в моделях - удалять все связанные сущности - было бы удобнее с ней писать (с другой стороны без этой фичи с sql хорошо потренеровался)
      
        - получилось использовать, но зачем нужен all (как хорошую практику рекомендуют в доке) - я не понимаю (зачем обновлять дочерние сущности при )
        
            неплохая статья - на русском даже:  https://www.peterspython.com/ru/blog/sqlalchemy-ispolzovanie-cascade-deletes-dlia-udaleniia-sviazannykh-obektov

            дока:
            The available cascades are ``save-update``, ``merge``,
            ``expunge``, ``delete``, ``delete-orphan``, and ``refresh-expire``.
            An additional option, ``all`` indicates shorthand for
            ``"save-update, merge, refresh-expir
        
        - что значит .scalar() в query sqlalchemy, почему это предпочтительно

      3) Разобраться, как работает автозакрытие сессий и Depends:
         - получается, что finally отрабатывает только после завершения search()
        >>> Есть ответ в Obsidian Fastapi/problem_session - на примере сравнения с Depends()



  II. Как всё готово (MVP есть):

  *) перенимать хорошие практики из реальных fastapi проектов - тут хорошо читается:
     https://github.com/nsidnev/fastapi-realworld-example-app/blob/master/app/api/dependencies/database.py

  ...) [По ходу других пунктов добавлять] 
    коды состояний возвращать и статус
    - CRUD.delete + @vr_app.delete('/groups/{id}', status_code=204)
      - уже в таком ключе писал 

    - коды состояний всякие бывают - почитать/видос, 
         204 - No Content - OK и доп. инфа не требуется для ответа (успешное удаление, например)
         400 - Bad Request

    >> Это уже шаг к RESTful principles 
       and provides clear feedback to the client regarding the outcome of their request

  1) валидировать ввод форм при создании/редактировании, а ещё поиск - чтоб SQL-инъекций не было  
    - email валидировать точно: not null (by model) + regexp
    - full_name для студентов - чтоб 3 слова было в строке

  2) Обвески/окружение
     - тестов добавить - pytest (покрыть методы)  
        - например нагрузочные: 
          groups/delete тестил в группе из 3 студентов и 33 - разницы нет - ~600мс, 250 человек - 2,5 секунды
                  - но при этом было раз, что 1,3 секунды удалялась група из 3 человек - т.е. внутри что-то тормозит

          >>> чтобы понять, что иногда тормозит - см. пункт ниже - там будут графики по всем ресурсам
              - можно БД логиировать и методы 
          
     - (не сложно это)  логгирование добавить - sentry (5 строк кода и на их фронте есть всевозможная аналитика с дашбордами - тот курс от Шумейко)
  
  *) поиграться с миграциями (например параметр nullable уточнив для таблиц) - alembic   
    - а то потом времени не будет в этом потренироватья, а ошибки тут недопустимы

    
  *) рефакторинг 
    - читаемость повысить, добавить ООП-патернов, мб архитектурно что-то изменить 
    - models, schemas - тоже в модуль организовать

  >>> БД - students_count автоматически считать мб можно
      - index - тоже вариант
      - это называется триггер) - есть смысл для надёжности использовать его
      - как вариант в models: (default = func.count(...))

  *) админку от fastapi добавить по корневому URL: GET API/
      - авторизацию настроить для админки, мб с jwt 
  
  **) что-то со скоростью создания сделать - ооочень долго идёт, мб с сессиями что или сервер с uvicorn сменить, мб параметры сервера покрутить - ресурсов юольше дать
    
  1000) !!! Dockerfile приложения написать и закинуть Image на DockerHub 
        + DockerCompose - чтоб БД тоже была
  *) есть бесплатные хостинги - можно туда залить
  
  III. Когда всё готово  
  Приложение функционирует, как раньше, всё круто,НО, 
  надо его облагородить:
    0) Redis подключить, в Fastapi достаточно декоратор будет навесить функциям: 6:20
        https://www.youtube.com/watch?v=Kr-V4IgJFes

        - мб посмотреть ещё в сторону других noSQL: ClickHouse, Cassandra

        !!! А вообще Redis очень круто развился и может собой всё остальное заменить - это не только про кеш - это будущее:

        - RediSearch
          Индексирует текст, а затем позволяет делать поиск по любым его частям за доли секунды на огромном объеме данных. По сути, заменяет вам ElasticSearch.

        - RedisJSON
          Позволяет хранить документы без четкой схемы в формате JSON, а также выполнять поиск по JSONPath и многое другое. В общем-то может заменить вам MongoDB.

        - RedisGraph
          Пишите соц. сеть и нужно быстро искать связи между юзерами? Для этого не нужно отдельной графовой БД типа Neo4j - модуль RedisGraph сделает все необходимое.

        - RedisTimeSeries
          Нужно подсохранить данные об аналитике, а затем удобно и быстро вытаскивать их по временным отрезкам для построения, например, графиков на них? RedisTimeSeries все решит, и не придется подрубать никаких Prometheus.

        - Redis Streams/Message Broker
          Нужно обрабатывать огромные потоки событий и иметь возможность масштабироваться? Этот модуль позволит использовать Redis не только, как БД, но и как брокер сообщений, такой как Kafka!        


    1) разделить приложение на два микросервиса (две отдельные кодовые бызы)
       как вариант на:
       - квесты и таски приходят извне => в отдельный проект сделать - с модульной структурой не сложно будет этот проект на 2 проекта разбить
       -группы
      + ещё фронт в отдельном контейнере
    
    * попробовать один из микросервисов на SOAP/GRPC сделать
    * на django/flask другие микросервисы написать
    
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

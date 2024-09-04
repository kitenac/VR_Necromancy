# Прогресс/План
- план описан в ветке dev\
в файле main.py - незакоменченным\
- ветка **async_pain** - асинхронная работа с бд (search/group, add/group - уже работают, сейчас проблема с использованием абстракции relation в students/add, мб заменю на явный запрос к БД)




# Documentation:
 - each file has **doc-string at top** - short summary
 - /docs, /redoc - auto docummentation for HTTP methods and schemas 

# Admin page for external entities - database manipulation
 - external entities: Tasks/Quests, StudentTasks/StudentQuests
 - avaliable at: {API_URL}/admin
 - bug_aware: do not use admin_page with internal entities CRUD-avaliable from frontend - it may give bugs (ex: student_count doesn`t change when adding new Student from admin_page)  

# Limitations
- OS: Linux-like:\
 due db-driver pymysql has **serious** problems with working on Windows (even after installing it can`t be found)

- browser(for frontend): \
  change default Refferr-Policy to no-referrer-when-downgrade (option 3 in Firefox) to send full Referer Header from frontend (otherwise group_id from client`s url will be not avaliable)  

- python: 3.12.1\

- [recomended] <use venv>

# Frontend image
https://hub.docker.com/repository/docker/albanec7/vr-pharmacy-client/general \
tag for my backend: PATCHED_API_ADDR

- if u want to specify different src API - follow PATCH section in dockerhub repo above 

# Start backend server:

## prod mode:
- run: docker-compose up 

## dev mode:
- Linux (WSL) 
  from directory where module located run (-m - module):\
   python3 -m VR_Necromancy.main 

- Windows:\
  serv is accessed via 127.0.0.1:8001 (after port forvarding)

## image building mode:
- specify in db_config.py:\
WORK_MODE = 'prod'\
\- it`s needed to access db image when app is run as container itself\

ps in future will move this configuration - as arguement on start of module


# Setup app
Some data supposed to go from external service (todo)
- so to populate Task`s page - go to {BACKEND}/docs 
    and set unacessable data handly at:\
      - post /quests/
      - post /tasks/


# BUG fix - Known frontend`s bug
groups aren`t displayed at Tasks page\
solution: add a quest as described in **Setup app**


# ------------- TODO PART ------------- 
>> Проброс портов должен помочь с доступам не только через localhost:\
Windows NAT workaround (doesnt works)

create\
netsh interface portproxy add v4tov4 listenport=8001 listenaddress=0.0.0.0 connectport=8001 connectaddress=172.27.166.175

show\
netsh interface portproxy show all

del\
netsh interface portproxy delete v4tov4 listenport=8001 listenaddress=127.0.0.7

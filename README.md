# Прогресс/План
- описан в ветке dev\
 в файле main.py - незакоменченным 

# Documentation:
 - each file has **doc-string at top** - short summary
 - /docs, /redoc - auto docummentation for HTTP methods and schemas 

# Frontend image
https://hub.docker.com/repository/docker/albanec7/vr-pharmacy-client/general \
tag for my backend: PATCHED_API_ADDR

- if u want to specify different src API - follow PATCH section in dockerhub repo above 


# Limitations
- OS: Linux-like:\
 due db-driver pymysql has **serious** problems with working on Windows (even after installing it can`t be found)

- browser(for frontend): \
  change default Refferr-Policy to no-referrer-when-downgrade (option 3 in Firefox) to send full Referer Header from frontend (otherwise group_id from client`s url will be not avaliable)  

- python: 3.12.1



# Start server:
- Linux (WSL)
 via 0.0.0.0:\
 cd ./vr_app \
 [recomended] <use venv>\
 uvicorn main:vr_app --host 0.0.0.0 --port 8001 

- Windows (cmd):\
  serv is accessed via 127.0.0.1:8001 


# ------------- TODO PART ------------- 
>> Проброс портов должен помочь с доступам не только через localhost:\
Windows NAT workaround (doesnt works)

create\
netsh interface portproxy add v4tov4 listenport=8001 listenaddress=0.0.0.0 connectport=8001 connectaddress=172.27.166.175

show\
netsh interface portproxy show all

del\
netsh interface portproxy delete v4tov4 listenport=8001 listenaddress=127.0.0.7

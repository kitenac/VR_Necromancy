FROM python:3.12-alpine
WORKDIR /vr_app

# coppy all files from cur dir to ./vr_app/VR_Necromancy | [NOTE] .dockerignore filters unnecessory files
COPY . ./VR_Necromancy

# gcc - needed for some libs, musl-dev - includes some needed C libs
RUN apk update && apk add gcc musl-dev
# Install the dependencies | [Note] happens on build => no need to reinstall it on each run 
# [reducing size] --no-cache-dir: pip won`t store the downloaded packages in its cache directory - This means that every time you run the pip install command, it will fetch the packages from the internet rather than using any previously cached versions.
RUN pip install --no-cache-dir -r ./VR_Necromancy/req.txt

ARG PORT=8001
ENV PORT=${PORT}

# exposing container from port given as arguemnt to container
EXPOSE $PORT

# start server at start of container
ENTRYPOINT [ "python3", "-m", "VR_Necromancy.main"]
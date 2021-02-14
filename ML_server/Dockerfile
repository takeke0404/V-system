FROM python:3.6
ARG project_dir=/ML_server/
COPY . ${project_dir}
WORKDIR ${project_dir}
RUN pip install -r requirements.txt && apt update && apt-get install -y ffmpeg

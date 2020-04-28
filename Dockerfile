FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /app/.
RUN pip install -r requirements.txt
COPY . /app


ENV ANNOTATIONINFOSERVICE_SETTINGS /app/annotationinfoservice/instance/docker_cfg.py
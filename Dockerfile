FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /app/.
RUN pip install -r requirements.txt
COPY . /app
COPY override/nginx.conf /etc/nginx/nginx.conf
COPY override/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV ANNOTATIONINFOSERVICE_SETTINGS /app/annotationinfoservice/instance/docker_cfg.py
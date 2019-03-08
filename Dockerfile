FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /app/.
RUN pip install numpy tornado==4.5.3 && \
    git clone -b fcc-fix2 --single-branch https://github.com/seung-lab/neuroglancer.git && \
    cd neuroglancer/python && \
    python setup.py develop && \
    cd /app && \
    pip install -r requirements.txt
COPY . /app


ENV ANNOTATIONINFOSERVICE_SETTINGS /app/annotationinfoservice/instance/docker_cfg.py
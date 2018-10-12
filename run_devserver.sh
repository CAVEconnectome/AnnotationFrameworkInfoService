#! /bin/bash 
export FLASK_APP=run.py
export FLASK_ENV=development
export ANNOTATIONINFOSERVICE_SETTINGS=$PWD/annotationinfoservice/instance/dev_config.py
flask run --port 9000

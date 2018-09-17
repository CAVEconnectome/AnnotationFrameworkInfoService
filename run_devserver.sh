#! /bin/bash 
export FLASK_APP=run.py
export FLASK_ENV=development
export ANNOTATIONINFOSERVICE_SETTINGS=$PWD/annotationinfo/instance/dev_config.py
flask run

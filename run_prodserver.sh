#! /bin/bash 
export FLASK_APP=run.py
export FLASK_ENV=development
export ANNOTATIONINFOSERVICE_SETTINGS=$PWD/annotationinfo/instance/prod_config.py
flask run

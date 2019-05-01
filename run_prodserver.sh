#! /bin/bash 
export FLASK_APP=run.py
export FLASK_ENV=development
export ANNOTATIONINFOSERVICE_SETTINGS=$PWD/annotationinfoservice/instance/prod_config.py
flask run

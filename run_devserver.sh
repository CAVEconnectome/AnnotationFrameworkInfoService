#! /bin/bash 
export FLASK_APP=run.py
export FLASK_ENV=development
export SYNAPSEDB_SETTINGS=$PWD/annotationinfo/instance/dev_config.py
flask run

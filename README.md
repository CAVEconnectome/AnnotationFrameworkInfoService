# AnnotationFrameworkInfoService

## Getting started
Install docker.

Edit annotationinfoservice/instance/config.cfg (see config.cfg.example) to include your deployment specific secret keys and neuroglancer server

```
  # spin up a postgres database on your localhost
  docker-compose up -d
  pip install -r requirements.txt
  python setup.py install
  ./run_devserver.sh
```

navigate to http://localhost:5000/admin for admin interface


## version 4.0 migration 
In version 4, the tablemapping and permission group models and associated API and UI elements were removed.  
This functionality was moved to the middle_auth service in version 2.13.0, and middle_auth_client was changed as of version 3.11.0 
to now use the endpoints available there to get the same functionality. 

This removed the awkward fact that "permission group" in the info service needed to match the "dataset" name in the auth service
but there was no enforcement.  Moving this data to the auth service was a better consolidation of related data. 

The flask admin UI elements for editing these tables are available now in the sticky_auth version of the middle_auth deployment at
DOMAIN/sticky_auth/flask_admin/.

If you are migrating to 4.0, you should first export your data and injest it into an upgraded version of auth.
Then you should upgrade all your services to the new version of middle_auth_client to use the data on auth.
Then you should upgrade the info service to drop this functionality from the info service.

If you are starting anew and don't have any data in the table_mapping and permission_group tables you can safely just deploy this service with no data. 

## changing models
If you change a model you need to setup a new flask migration script to upgrade the models from the present version to the new version.
To do this you need to have a database running that contains the models as they are before your change. 

In CAVEdeployment this can be done by connecting to a current production database using ./infrastructure/global/run_cloud_sql_proxy.sh DEPLOYMENT_NAME

this will setup a database running on your local computer using docker on port 3306.

you should have a local environment file setup to help configure your system to connect properly

I have a file called .prod.env for this.. You will have to replace YOUR_PASSWORD_HERE and global.daf-apis.com with the values that are appropriate for your deployment

```
  export POSTGRES_USER=postgres
  export POSTGRES_PASSWORD=YOUR_PASSWORD_HERE
  export POSTGRES_DB=annotation

  export AUTH_URI=global.daf-apis.com/auth
  export STICKY_AUTH_URL=global.daf-apis.com/sticky_auth
  export INFO_URL=global.daf-apis.com/info
  export ANNOTATIONINFOSERVICE_SETTINGS=prod_config.py
  export FLASK_APP=run.py
```

prod_config.py needs to go in annotationinfoservice/instance/prod_config.py and looks like..
NOTE: replace YOUR_PASSWORD_HERE with your postgres password

```
  CSRF_SESSION_KEY = "YOURREALSECRETCSRF"
  SECRET_KEY = b"YOURREALSECRETKEY"
  SQLALCHEMY_DATABASE_URI = (
      "postgres://postgres:YOUR_PASSWORD_HERE@127.0.0.1:3306/infoservice"
  )
  NEUROGLANCER_URL = "https://neuromancer-seung-import.appspot.com"
  AUTH_RAISE_WZ_EXCEPTION = True
  AUTH_TOKEN = "PICK_A_RANDOM_TOKEN"
```
once these files are in place you should be able to run 

```
  flask db migrate -m "A MESSAGE ABOUT WHAT WAS CHANGED"
```

This should create a new migration file in ./migrations/versions/  called XXXXX_A_MESSAGE_ABOUT_WHAT_WAS_CHANGED.py where XXXXXX is the migration_id of the migration. 
You should inspect this file to make sure that the script makes sense for what was changed before commiting. 




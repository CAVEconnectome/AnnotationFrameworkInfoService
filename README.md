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


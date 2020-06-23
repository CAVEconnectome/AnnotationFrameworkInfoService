from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from annotationinfoservice.datasets.models import DataStack,\
     TableMapping, PermissionGroup, AlignedVolume
from middle_auth_client import auth_requires_admin
from flask import redirect

@auth_requires_admin
def test_super_admin():
     return "is_super_admin"

class SuperAdminView(ModelView):
     
     def is_accessible(self):
          resp = test_super_admin()
          if resp=="is_super_admin":
               return True    
          else:
               return False
               
     def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('views.index', next=request.url))

def setup_admin(app, db):
    admin = Admin(app, name="infoservice admin", url='/info/admin')
    admin.add_view(SuperAdminView(AlignedVolume, db.session))
    admin.add_view(SuperAdminView(DataStack, db.session))
    admin.add_view(SuperAdminView(PermissionGroup, db.session))
    admin.add_view(SuperAdminView(TableMapping, db.session))
    
    return admin

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from annotationinfoservice.datasets.models import DataStack,\
     TableMapping, PermissionGroup, AlignedVolume
from middle_auth_client import auth_requires_admin, auth_required
from flask import redirect, url_for, request, g

class SuperAdminView(ModelView):
     @auth_required
     def is_accessible(self):
        return g.auth_user['admin']
               
     def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('admin.index'))

def setup_admin(app, db):
    admin = Admin(app, name="infoservice admin", url='/info/admin')
    admin.add_view(SuperAdminView(AlignedVolume, db.session))
    admin.add_view(SuperAdminView(DataStack, db.session))
    admin.add_view(SuperAdminView(PermissionGroup, db.session))
    admin.add_view(SuperAdminView(TableMapping, db.session))
    
    return admin

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from annotationinfoservice.datasets.models import DataStack,\
     TableMapping, PermissionGroup, AlignedVolume


def setup_admin(app, db):
    admin = Admin(app, name="annotationinfoservice")
    admin.add_view(ModelView(AlignedVolume, db.session))
    admin.add_view(ModelView(DataStack, db.session))
    admin.add_view(ModelView(PermissionGroup, db.session))
    admin.add_view(ModelView(TableMapping, db.session))
    
    return admin

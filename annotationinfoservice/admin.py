from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from annotationinfoservice.datasets.models import DataSet, PyChunkedGraphTable


def setup_admin(app, db):
    admin = Admin(app, name="annotationinfoservice")
    admin.add_view(ModelView(DataSet, db.session))
    admin.add_view(ModelView(PyChunkedGraphTable, db.session))
    return admin

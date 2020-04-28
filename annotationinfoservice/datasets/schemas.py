import annotationinfoservice.datasets.models as models
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class DataSetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.DataSet

class DataSetSchemaV2(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.DataSetV2

class PermissionGroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.PermissionGroup
        
class TableMappingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.TableMapping
        include_fk = True

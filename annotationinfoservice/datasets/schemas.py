import annotationinfoservice.datasets.models as models
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class DataSetSchema(ma.ModelSchema):
    class Meta:
        model = models.DataSet

import annotationinfoservice.datasets.models as models
from flask_marshmallow import Marshmallow

ma = Marshmallow()



class SimpleDatasetSchema(ma.ModelSchema):
    class Meta:
        model = models.DataSet
        fields = ['name','id']

class PyChunkedGraphTableSchema(ma.ModelSchema):
    dataset = ma.Nested(SimpleDatasetSchema)
    class Meta:
        model = models.PyChunkedGraphTable

class SimplePyChunkedGraphTableSchema(ma.ModelSchema):
    class Meta:
        model = models.PyChunkedGraphTable
        fields = ['name']

class DataSetSchema(ma.ModelSchema):
    pcg_tables = ma.Nested(SimplePyChunkedGraphTableSchema, many=True)
    class Meta:
        model = models.DataSet
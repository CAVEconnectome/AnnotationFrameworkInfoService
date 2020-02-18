import annotationinfoservice.datasets.models as models
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class DataSetSchema(ma.ModelSchema):
    class Meta:
        model = models.DataSet

class DataSetSchema2(ma.ModelSchema):
    class Meta:
        fields = ('name',
                  'image_path',
                  'segmentation_path',
                  'synapse_table',
                  'soma_table',
                  'analysis_database',
                  'viewer_site')
        model = models.DataSet
        
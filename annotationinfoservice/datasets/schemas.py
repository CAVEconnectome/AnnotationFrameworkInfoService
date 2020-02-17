import annotationinfoservice.datasets.models as models
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class DataSetSchema(ma.ModelSchema):
    class Meta:
        model = models.DataSet

class DataSetSchema2(ma.ModelSchema):
    class Meta:
        fields = ('name',
                  'image_source',
                  'flat_segmentation_source',
                  'graphene_source',
                  'synapse_segmentation_source',
                  'analysis_database_ip')
        model = models.DataSet
        
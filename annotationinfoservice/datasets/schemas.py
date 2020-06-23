import annotationinfoservice.datasets.models as models
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class AlignedVolumeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.AlignedVolume

class DataStackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.DataStack
        
    aligned_volume = ma.HyperlinkRelated("api.Annotation Infoservice_aligned_volume_id_resource", "id")

class PermissionGroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.PermissionGroup
        
class TableMappingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.TableMapping
    
    

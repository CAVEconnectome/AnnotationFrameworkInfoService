import annotationinfoservice.datasets.models as models
from flask_marshmallow import Marshmallow
import marshmallow

ma = Marshmallow()


class ImageSourceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.ImageSource


class AlignedVolumeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.AlignedVolume


class DataStackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.DataStack

    aligned_volume = ma.HyperlinkRelated(
        "api.Annotation Infoservice_aligned_volume_id_resource", "id"
    )


class DataStackSchemaFull(marshmallow.Schema):
    aligned_volume = marshmallow.fields.Nested(AlignedVolumeSchema)
    segmentation_source = marshmallow.fields.String()
    skeleton_source = marshmallow.fields.String()
    analysis_database = marshmallow.fields.String()
    viewer_site = marshmallow.fields.String()
    synapse_table = marshmallow.fields.String()
    soma_table = marshmallow.fields.String()
    local_server = marshmallow.fields.String()
    description = marshmallow.fields.String()
    viewer_resolution_x = marshmallow.fields.Float()
    viewer_resolution_y = marshmallow.fields.Float()
    viewer_resolution_z = marshmallow.fields.Float()
    proofreading_status_table = marshmallow.fields.String()
    cell_identification_table = marshmallow.fields.String()
    proofreading_review_table = marshmallow.fields.String()

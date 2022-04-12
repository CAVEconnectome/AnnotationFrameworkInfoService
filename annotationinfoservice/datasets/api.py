# Import flask dependencies
from flask import jsonify, render_template, current_app, make_response, Blueprint
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from annotationinfoservice.datasets import schemas
from annotationinfoservice.datasets.service import (
    DataStackService,
    AlignedVolumeService,
)
from typing import List
from middle_auth_client import (
    auth_required,
    auth_requires_permission,
    user_has_permission,
)

__version__ = "4.0.0"


authorizations = {
    "apikey": {"type": "apiKey", "in": "query", "name": "middle_auth_token"}
}

api_bp = Namespace(
    "Annotation Infoservice", authorizations=authorizations, description="Infoservice"
)


@api_bp.route("/aligned_volume")
@api_bp.doc("get aligned_volumes", security="apikey")
class AlignedVolumeResource(Resource):
    """Aligned Volume System Info"""

    @auth_required
    def get(self) -> List:
        """Get all Aligned Volumes"""
        aligned_vols = [
            a
            for a in AlignedVolumeService.get_all()
            if user_has_permission("view", a.name, "aligned_volume")
        ]

        return [av["name"] for av in aligned_vols]


@api_bp.route("/aligned_volume/id/<int:id>")
@api_bp.param("id", "AlignedVolume Id")
class AlignedVolumeIdResource(Resource):
    """AlignedVolume by Id"""

    @api_bp.doc("get aligned_volume by id", security="apikey")
    @responds(schema=schemas.AlignedVolumeSchema)
    def get(self, id: int) -> schemas.AlignedVolumeSchema:
        """Get Aligned Volume By Id"""
        return AlignedVolumeService.get_aligned_volume_by_id(id)


@api_bp.route("/aligned_volume/<string:aligned_volume_name>")
@api_bp.param("aligned_volume_name", "AlignedVolume Name")
class AlignedVolumeNameResource(Resource):
    """Aligned Volume by Name"""

    @api_bp.doc("get aligned_volume", security="apikey")
    @responds(schema=schemas.AlignedVolumeSchema)
    @auth_requires_permission(
        "view", table_arg="aligned_volume_name", resource_namespace="aligned_volume"
    )
    def get(self, aligned_volume_name: str) -> schemas.AlignedVolumeSchema:
        """Get AlignedVolume By Name"""
        return AlignedVolumeService.get_aligned_volume_by_name(aligned_volume_name)


@api_bp.route("/aligned_volume/<string:aligned_volume_name>/datastacks")
@api_bp.param("aligned_volume_name", "AlignedVolume Name")
class DataStacksInAlignedVolumesResource(Resource):
    """DataStacks in an Aligned Volume by Name"""

    @api_bp.doc("get datastacks in aligned_volume", security="apikey")
    @auth_required
    def get(self, aligned_volume_name: str) -> List[str]:
        """Get DataStacks in an Aligned Volume by Name"""
        av = AlignedVolumeService.get_aligned_volume_by_name(aligned_volume_name)
        ds = DataStackService.get_datastacks_by_aligned_volume_id(av.id)
        return [d.name for d in ds if user_has_permission("view", d.name, "datastack")]


@api_bp.route("/datastacks")
class DataStackResource(Resource):
    """Dataset Info"""

    @api_bp.doc("get datastacks", security="apikey")
    @auth_required
    def get(self) -> List:
        """Get all Datastacks"""
        datastacks = DataStackService.get_all()
        return [
            datastack["name"]
            for datastack in datastacks
            if user_has_permission("view", datastack["name"], "datastack")
        ]


@api_bp.route("/datastack/<string:datastack>")
@api_bp.param("datastack", "DataStack Name")
class DataStackNameResource(Resource):
    """DataStack by Name"""

    @responds(schema=schemas.DataStackSchema)
    @api_bp.doc("get datastack", security="apikey")
    @auth_requires_permission(
        "view", table_arg="datastack", resource_namespace="datastack"
    )
    def get(self, datastack: str) -> schemas.DataStackSchema:
        """Get DataStack By Name"""

        return DataStackService.get_datastack_by_name(datastack)


@api_bp.route("/datastack/full/<string:datastack>")
@api_bp.param("datastack", "DataStack Name")
class DataStackNameFullResource(Resource):
    """DataStack by Name with AlignedVolume"""

    @responds(schema=schemas.DataStackSchemaFull)
    @api_bp.doc("get datastack full", security="apikey")
    @auth_requires_permission(
        "view", table_arg="datastack", resource_namespace="datastack"
    )
    def get(self, datastack: str) -> schemas.DataStackSchemaFull:
        """Get DataStack By Name with AlignedVolume Details"""
        ds = DataStackService.get_datastack_by_name(datastack)
        return ds

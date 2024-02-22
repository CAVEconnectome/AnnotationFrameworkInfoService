# Import flask dependencies
from flask import jsonify, render_template, current_app, make_response, Blueprint
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from annotationinfoservice.datasets import schemas
from annotationinfoservice.datasets.service import (
    DataStackService,
    TableMappingService,
    PermissionGroupService,
    AlignedVolumeService,
    ImageSourceService,
)
from typing import List
from middle_auth_client import (
    auth_required,
    auth_requires_permission,
    user_has_permission,
)

__version__ = "3.17.1"


authorizations = {
    "apikey": {"type": "apiKey", "in": "query", "name": "middle_auth_token"}
}

api_bp = Namespace(
    "Annotation Infoservice", authorizations=authorizations, description="Infoservice"
)


@api_bp.route("/ngl_info")
@api_bp.doc("get ngl_info", security="apikey")
class NGLInfoResource(Resource):
    """NGL Info. Get all the information about what datasets a user has access to
    for ngl_extend e to configure itself"""

    @auth_required
    def get(self) -> List:
        """Get all NGL Info"""
        aligned_vols = [
            a
            for a in AlignedVolumeService.get_all()
            if user_has_permission("view", a.name, "aligned_volume")
        ]
        datastacks = {}
        image_sources = {}
        return_json = {}
        for av in aligned_vols:
            datastacks = DataStackService.get_datastacks_by_aligned_volume_id(av.id)
            datastacks = [
                d
                for d in datastacks
                if user_has_permission("view", d.name, "datastack")
            ]

            image_sources = ImageSourceService.get_image_sources_by_av(av.id)
            if len(image_sources) == 0:
                base_source = {
                    "image_source": av.image_source,
                    "ngl_image_name": "img",
                    "name": av.name,
                    "description": av.description,
                }

                image_layers = [base_source]
            else:
                image_layers = []
                for img_src in image_sources:
                    image_layers.append(
                        {
                            "image_source": img_src.image_source,
                            "ngl_image_name": img_src.name,
                            "name": img_src.name,
                            "description": img_src.description,
                        }
                    )

            segmentation_layers = []
            for datastack in datastacks:
                d = {
                        "name": datastack.name,
                        "description": datastack.description,
                        "segmentation_source": datastack.segmentation_source
                    }
                if datastack.base_link_id is not None:
                    d["initial_state_id"] = datastack.base_link_id 
                segmentation_layers.append(d)
            if av.display_name is not None:
                name = av.display_name
            else:
                name = av.name
            return_json[name] = {
                "image_layers": image_layers,
                "segmentation_layers": segmentation_layers,
                "description": av.description,
            }

        return return_json


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


@api_bp.route("/permissiongroups")
class PermissionGroupResource(Resource):
    """Permission Groups"""

    @api_bp.doc("get permission groups", security="apikey")
    @auth_required
    def get(self) -> List[str]:
        """Get All Permissions Groups"""
        pgs = PermissionGroupService.get_all()
        return [pg.name for pg in pgs]


@api_bp.route("/permissiongroup/name/<string:pg_name>")
@api_bp.param("pg_name", "Permission Group Name")
class PermissionGroupNameResource(Resource):
    """Permission Group by Name"""

    @responds(schema=schemas.PermissionGroupSchema)
    @api_bp.doc("get permission group", security="apikey")
    @auth_required
    def get(self, pg_name: str) -> schemas.PermissionGroupSchema:
        """Get Permissions Group by Name"""

        return PermissionGroupService.get_permission_group_by_name(pg_name)


@api_bp.route("/permissiongroup/id/<int:id>")
@api_bp.param("id", "PermissionGroup Id")
class PermissionGroupIdResource(Resource):
    """PermissionGroup by Id"""

    @api_bp.doc("get permissiongroup by id", security="apikey")
    @responds(schema=schemas.PermissionGroupSchema)
    @auth_required
    def get(self, id: int) -> schemas.PermissionGroupSchema:
        """Get Permission Group By Id"""
        return PermissionGroupService.get_by_id(id)


@api_bp.route("/tablemapping")
class TableMappingResource(Resource):
    """Table Mapping"""

    @responds(schema=schemas.TableMappingFullSchema(many=True))
    @api_bp.doc("get table mappings", security="apikey")
    @auth_required
    def get(self) -> schemas.TableMappingFullSchema:
        """Get All Table Maps"""
        return TableMappingService.get_all()


@api_bp.route("/tablemapping/service/<string:service_name>")
@api_bp.param("service_name", "Service Name")
class TableMappingNameResource(Resource):
    """Table Mapping by Service Name"""

    @responds(schema=schemas.TableMappingSchema(many=True))
    @api_bp.doc("get table mappings by service", security="apikey")
    @auth_required
    def get(self, service_name: str) -> schemas.TableMappingFullSchema:
        """Get Table Mappings From Service"""
        return TableMappingService.get_by_service(service_name)


@api_bp.route("/tablemapping/service/<string:service_name>/table/<string:table_name>")
@api_bp.param("service_name", "Service Name")
@api_bp.param("table_name", "Table Name")
class TableMappingGroupResource(Resource):
    """Table Map Group by Service and Table Name"""

    @responds(schema=schemas.TableMappingFullSchema)
    @api_bp.doc("get table mapping group", security="apikey")
    @auth_required
    def get(self, service_name: str, table_name: str) -> schemas.TableMappingFullSchema:
        """Get Table Map Group by Service and Table Name"""
        table_map = TableMappingService.get_permission_group_from_table_and_service(
            table_name, service_name
        )
        return table_map


@api_bp.route(
    "/tablemapping/service/<string:service_name>/table/<string:table_name>/permission_group"
)
@api_bp.param("service_name", "Service Name")
@api_bp.param("table_name", "Table Name")
class PermissionGroupForTableMappingResource(Resource):
    """Get Permission Group for a Table Mapping by Service and Table Name"""

    @api_bp.doc("get table mapping group", security="apikey")
    def get(self, service_name: str, table_name: str) -> str:
        """Get Permission Group of Table Map Group by Service and Table Name"""
        table_map = TableMappingService.get_permission_group_from_table_and_service(
            table_name, service_name
        )
        return table_map.permission_group.name

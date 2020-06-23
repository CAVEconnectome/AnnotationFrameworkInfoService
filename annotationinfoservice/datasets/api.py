# Import flask dependencies
from flask import jsonify, render_template, current_app, make_response, Blueprint
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from annotationinfoservice.datasets.schemas import DataStackSchema, TableMappingSchema, PermissionGroupSchema, AlignedVolumeSchema
from annotationinfoservice.datasets.service import DataStackService, TableMappingService, PermissionGroupService, AlignedVolumeService
from typing import List


__version__ = "0.4.0"

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'query',
        'name': 'middle_auth_token'
    }
}

api_bp = Namespace("Annotation Infoservice",
                   authorizations=authorizations,
                   description="Infoservice")

@api_bp.route("/aligned_volume")
@api_bp.doc('get aligned_volumes', security='apikey')
class AlignedVolumeResource(Resource):
    """Aligned Volume System Info"""

    def get(self) -> List:
        """Get all Aligned Volumes """
        aligned_vols =  AlignedVolumeService.get_all()
        return [av['name'] for av in aligned_vols] 

@api_bp.route("/aligned_volume/id/<int:id>")
@api_bp.param("id", "AlignedVolume Id")
class AlignedVolumeIdResource(Resource):
    """AlignedVolume by Name"""

    @api_bp.doc('get aligned_volume by id', security='apikey')
    @responds(schema=AlignedVolumeSchema)
    def get(self, id: int) -> AlignedVolumeSchema:
        """Get Aligned Volume By Name"""
        return AlignedVolumeService.get_aligned_volume_by_id(id)

@api_bp.route("/aligned_volume/<string:aligned_volume_name>")
@api_bp.param("aligned_volume_name", "AlignedVolume Name")
class AlignedVolumeNameResource(Resource):
    """Aligned Volume by Name"""

    @api_bp.doc('get aligned_volume', security='apikey')
    @responds(schema=AlignedVolumeSchema)
    def get(self, aligned_volume_name: str) -> AlignedVolumeSchema:
        """Get AlignedVolume By Name"""
        return AlignedVolumeService.get_aligned_volume_by_name(aligned_volume_name)

@api_bp.route("/datastacks")
class DataStackResource(Resource):
    """Dataset Info"""

    @api_bp.doc('get datastacks', security='apikey')
    def get(self) -> List:
        """Get all Datastacks """
        datastacks =  DataStackService.get_all()
        return [datastack['name'] for datastack in datastacks] 

@api_bp.route("/datastack/<string:datastack>")
@api_bp.param("datastack", "DataStack Name")
class DataStackNameResource(Resource):
    """DataStack by Name"""

    @responds(schema=DataStackSchema)
    @api_bp.doc('get datastack', security='apikey')
    def get(self, datastack: str) -> DataStackSchema:
        """Get DataStack By Name"""

        return DataStackService.get_datastack_by_name(datastack)

@api_bp.route("/permissiongroups")
class PermissionGroupResource(Resource):
    """Permission Groups"""

    @api_bp.doc('get permission groups', security='apikey')
    def get(self) -> List[str]:
        """Get All Permissions Groups"""
        pgs = PermissionGroupService.get_all()
        return [pg.name for pg in pgs]

@api_bp.route("/permissiongroup/name/<string:pg_name>")
@api_bp.param("pg_name", "Permission Group Name")
class PermissionGroupNameResource(Resource):
    """Permission Group by Name"""

    @responds(schema=PermissionGroupSchema)
    @api_bp.doc('get permission group', security='apikey')
    def get(self, pg_name: str) -> PermissionGroupSchema:
        """Get Permissions Group by Name"""

        return PermissionGroupService.get_permission_group_by_name(pg_name)

@api_bp.route("/tablemapping")
class TableMappingResource(Resource):
    """Table Mapping"""

    @api_bp.doc('get table mappings', security='apikey')
    def get(self) -> List[str]:
        """Get All Table Maps"""
        return TableMappingService.get_all()

@api_bp.route("/tablemapping/service/<string:service_name>")
@api_bp.param("service_name", "Service Name")
class TableMappingNameResource(Resource):
    """Table Mapping by Service Name"""

    @responds(schema=TableMappingSchema(many=True))
    @api_bp.doc('get table mappings by service', security='apikey')
    def get(self, service_name: str) -> TableMappingSchema:
        """Get Table Mappings From Service"""
        return TableMappingService.get_by_service(service_name)

@api_bp.route("/tablemapping/service/<string:service_name>/table/<string:table_name>")
@api_bp.param("service_name", "Service Name")
@api_bp.param("table_name", "Table Name")
class TableMappingGroupResource(Resource):
    """Table Map Group by Service and Table Name"""

    @responds(schema=TableMappingSchema)
    @api_bp.doc('get table mapping group', security='apikey')
    def get(self, service_name: str, table_name: str) -> TableMappingSchema:
        """Get Table Map Group by Service and Table Name"""
        return TableMappingService.get_permission_group_from_table_and_service(service_name, table_name)
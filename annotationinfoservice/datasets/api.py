# Import flask dependencies
from flask import jsonify, render_template, current_app, make_response, Blueprint
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from annotationinfoservice.datasets.models import DataSet, DataSetV2, PermissionGroup, TableMapping
from annotationinfoservice.datasets.schemas import DataSetSchema, DataSetSchemaV2, TableMappingSchema, PermissionGroupSchema
from annotationinfoservice.datasets.service import DatasetService, TableMappingService, PermissionGroupService
from typing import List


__version__ = "0.4.0"

api_bp = Namespace("Annotation Infoservice", description="Infoservice")


@api_bp.route("/datasets")
class DatasetResource(Resource):
    """Dataset Info"""

    def get(self) -> List:
        """Get all Datasets """
        datasets =  DatasetService.get_all()
        return [dataset['name'] for dataset in datasets] 

@api_bp.route("/dataset/<string:dataset>")
@api_bp.param("dataset", "Dataset Name")
class DatasetNameResource(Resource):
    """Dataset by Name"""

    @responds(schema=DataSetSchemaV2)
    def get(self, dataset: str) -> DataSetSchemaV2:
        """Get Dataset By Name"""

        return DatasetService.get_dataset_by_name(dataset)

@api_bp.route("/permissiongroups")
class PermissionGroupResource(Resource):
    """Permission Groups"""

    def get(self) -> List[PermissionGroup]:
        """Get All Permissions Groups"""
        pgs = PermissionGroupService.get_all()
        return [pg.name for pg in pgs]

@api_bp.route("/permissiongroup/name/<string:pg_name>")
@api_bp.param("pg_name", "Permission Group Name")
class PermissionGroupNameResource(Resource):
    """Permission Group by Name"""

    @responds(schema=PermissionGroupSchema)
    def get(self, pg_name: str) -> PermissionGroupSchema:
        """Get Permissions Groups by Name"""

        return PermissionGroupService.get_permission_group_by_name(pg_name)

@api_bp.route("/tablemapping")
class TableMappingResource(Resource):
    """Table Mapping"""

    def get(self) -> List[TableMapping]:
        """Get All Table Maps"""
        return TableMappingService.get_all()

@api_bp.route("/tablemapping/service/<string:service_name>")
@api_bp.param("service_name", "Service Name")
class TableMappingNameResource(Resource):
    """Table Mapping by Service Name"""

    @responds(schema=TableMappingSchema)
    def get(self, service_name: str) -> TableMappingSchema:
        """Get Table Mappings From Service"""
        return TableMappingService.get_by_service(service_name)
@api_bp.route("/tablemapping/service/<string:service_name>/table/<string:table_name>")
@api_bp.param("service_name", "Service Name")
@api_bp.param("table_name", "Table Name")
class TableMappingGroupResource(Resource):
    """Table Map Group by Service and Table Name"""

    @responds(schema=TableMappingSchema)
    def get(self, service_name: str, table_name: str) -> TableMappingSchema:
        """Get Table Map Group by Service and Table Name"""
        return TableMappingService.get_permission_group_from_table_and_service(service_name, table_name)
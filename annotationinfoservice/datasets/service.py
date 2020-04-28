from typing import List
from annotationinfoservice.datasets.models import DataSetV2, PermissionGroup, TableMapping
from annotationinfoservice.datasets.schemas import DataSetSchemaV2, PermissionGroupSchema, TableMappingSchema 

class DatasetService:
    @staticmethod
    def get_all() -> List[DataSetV2]:
        return DataSetV2.query.all()

    @staticmethod
    def get_dataset_by_name(dataset: str) -> DataSetV2:
        dataset = DataSetV2.query.filter_by(name=dataset).first_or_404()
        return dataset


class PermissionGroupService:
    @staticmethod
    def get_all() -> List[PermissionGroup]:
        return PermissionGroup.query.all()

    @staticmethod
    def get_by_id(id: int) -> PermissionGroup:
        return PermissionGroup.query.get(id)

    @staticmethod
    def get_permissiongroup_by_name(pg_name: str) -> PermissionGroup:
        pg = PermissionGroup.query.filter_by(name=pg_name).first_or_404()
        # schema = PermissionGroupSchema()
        return pg


class TableMappingService:
    @staticmethod
    def get_all() -> List[TableMapping]:
        return TableMapping.query.all()

    @staticmethod
    def get_by_service(service_name: str) -> TableMapping:
        return TableMapping.query.filter_by(service_name=service_name).all()

    @staticmethod
    def get_permission_group_from_table_and_service(table_name: str, service_name: str):
        return TableMapping.query.filter_by(table_name=table_name, service_name=service_name).first_or_404()

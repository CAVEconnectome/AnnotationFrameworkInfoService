from typing import List
from annotationinfoservice.datasets.models import DataSetV2, PermissionGroup, TableMapping
from annotationinfoservice.datasets.schemas import DataSetSchemaV2, PermissionGroupSchema, TableMappingSchema 

class DatasetService:
    @staticmethod
    def get_all() -> List[DataSetV2]:
        return DataSetV2.query.all()

    @staticmethod
    def get_dataset_by_name(dataset: str) -> DataSetV2:
        return DataSetV2.query.filter_by(name=dataset).first_or_404()


class PermissionGroupService:
    @staticmethod
    def get_all() -> List[PermissionGroup]:
        return PermissionGroup.query.all()

    @staticmethod
    def get_by_id(id: int) -> PermissionGroup:
        return PermissionGroup.query.get(id)

    @staticmethod
    def get_permission_group_by_name(pg_name: str) -> PermissionGroup:
        return PermissionGroup.query.filter_by(name=pg_name).first_or_404()


class TableMappingService:
    @staticmethod
    def get_all() -> List[TableMapping]:
        tables = TableMapping.query.all()
        schema = TableMappingSchema(many=True)
        return schema.dump(tables)

    @staticmethod
    def get_by_service(service_name: str) -> List[TableMapping]:
        table_service = TableMapping.query.filter_by(service_name=service_name).all()
        schema = TableMappingSchema(many=True)
        print(f"SCHEMA {schema}")
        return schema.dump(table_service)

    @staticmethod
    def get_permission_group_from_table_and_service(table_name: str, service_name: str) -> TableMapping:
        table_service_name = TableMapping.query.filter_by(table_name=table_name, service_name=service_name).first_or_404()
        schema = TableMappingSchema()
        return schema.dump(table_service_name)
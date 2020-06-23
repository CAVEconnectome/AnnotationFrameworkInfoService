from typing import List
from annotationinfoservice.datasets.models import DataStack, PermissionGroup, TableMapping, AlignedVolume
from annotationinfoservice.datasets.schemas import DataStackSchema, PermissionGroupSchema, TableMappingSchema , AlignedVolumeSchema

class AlignedVolumeService:
    @staticmethod
    def get_all() -> List[AlignedVolume]:
        return AlignedVolume.query.all()

    @staticmethod
    def get_aligned_volume_by_name(aligned_volume_name: str) -> AlignedVolume:
        return AlignedVolume.query.filter_by(name=aligned_volume_name).first_or_404()

    @staticmethod
    def get_aligned_volume_by_id(id: int) -> AlignedVolume:
        return AlignedVolume.query.filter_by(id=id).first_or_404()

class DataStackService:
    @staticmethod
    def get_all() -> List[DataStack]:
        return DataStack.query.all()

    @staticmethod
    def get_datastack_by_name(datastack: str) -> DataStack:
        return DataStack.query.filter_by(name=datastack).first_or_404()

    @staticmethod
    def get_datastacks_by_aligned_volume_id(aligned_volume_id: int) -> List[DataStack]:
        return DataStack.query.filter_by(aligned_volume_id = aligned_volume_id).all()


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
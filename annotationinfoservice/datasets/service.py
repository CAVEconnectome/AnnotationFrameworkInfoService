from typing import List
from annotationinfoservice.datasets.models import (
    DataStack,
    AlignedVolume,
)
from annotationinfoservice.datasets.schemas import (
    DataStackSchema,
    AlignedVolumeSchema,
)


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


class ImageSourceService:
    @staticmethod
    def get_all() -> List[ImageSource]:
        return ImageSource.query.all()

    @staticmethod
    def get_image_sources_by_av(aligned_volume_id: id) -> List[ImageSource]:
        return ImageSource.query.filter_by(aligned_volume_id=aligned_volume_id).all()


class DataStackService:
    @staticmethod
    def get_all() -> List[DataStack]:
        return DataStack.query.all()

    @staticmethod
    def get_datastack_by_name(datastack: str) -> DataStack:
        return DataStack.query.filter_by(name=datastack).first_or_404()

    @staticmethod
    def get_datastacks_by_aligned_volume_id(aligned_volume_id: int) -> List[DataStack]:
        return DataStack.query.filter_by(aligned_volume_id=aligned_volume_id).all()

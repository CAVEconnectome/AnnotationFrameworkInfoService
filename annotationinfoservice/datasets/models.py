from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from annotationinfoservice.database import Base


class NamedModel(object):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    def __repr__(self):
        return "{}({})".format(self.name, self.id)

    
    def __getitem__(self, field):
        return self.__dict__[field]

class DataSet(NamedModel, Base):
    __tablename__ = "dataset"
    image_source = Column(String(200), nullable=False)
    flat_segmentation_source = Column(String(200), nullable=True)
    pychunkgraph_segmentation_source = Column(String(200), nullable=True)
    pychunkgraph_endpoint = Column(String(200), nullable=True)
    annotation_engine_endpoint = Column(String(200), nullable=True)
    synapse_segmentation_source = Column(String(200), nullable=True)
    pychunkedgraph_viewer_source = Column(String(200), nullable=True)
    graphene_source = Column(String(200), nullable=True)
    pychunkedgraph_supervoxel_source = Column(String(200), nullable=True)
    analysis_database_ip = Column(String(100), nullable=True)

class AlignedVolume(NamedModel, Base):
    __tablename__ = "aligned_volume"
    description = Column(String(500), nullable=True)
    image_source = Column(String(200), nullable=False)
    # preferred_stack_id = Column(Integer, ForeignKey('datastack.id'))
    # preferred_stack = relationship("DataStack")

class DataStack(NamedModel, Base):
    __tablename__ = "datastack"
    aligned_volume_id = Column(Integer, ForeignKey('aligned_volume.id'))
    aligned_volume = relationship("AlignedVolume")
    segmentation_source = Column(String(200), nullable=True)
    analysis_database = Column(String(100), nullable=True)
    viewer_site = Column(String(200), nullable=True)
    synapse_table= Column(String(100), nullable=True)
    soma_table = Column(String(100), nullable=False)
    local_server = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)

class PermissionGroup(NamedModel, Base):
    __tablename__ = "permissiongroup"
    
class TableMapping(Base):
    __tablename__ = "tablemapping"
    id = Column(Integer, primary_key=True)
    table_name = Column(String(100), nullable=False)
    service_name = Column(String(100), nullable=False)
    permissiongroup_id = Column(Integer, ForeignKey('permissiongroup.id'))
    permissiongroup = relationship("PermissionGroup")
from sqlalchemy import Column, Integer, String, ForeignKey
from annotationinfoservice.database import Base
from sqlalchemy.orm import relationship


class NamedModel(object):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    def __repr__(self):
        return "{}({})".format(self.name, self.id)


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
    pcg_tables = relationship("PyChunkedGraphTable")
    
class PyChunkedGraphTable(NamedModel, Base):
    __tablename__ = "pcg_tables"
    dataset_id = Column(Integer, ForeignKey('dataset.id'))
    dataset =  relationship("DataSet", back_populates="pcg_tables")
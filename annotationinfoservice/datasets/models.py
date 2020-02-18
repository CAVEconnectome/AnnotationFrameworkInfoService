from sqlalchemy import Column, Integer, String
from annotationinfoservice.database import Base


class NamedModel(object):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return "{}({})".format(self.name, self.id)


class DataSet(NamedModel, Base):
    __tablename__ = "dataset"
    image_path = Column(String(200), nullable=False)
    segmentation_path = Column(String(200), nullable=True)
    analysis_database = Column(String(100), nullable=True)
    viewer_site = Column(String(200), nullable=True)
    synapse_table= Column(String(100), nullable=True)
    soma_table = Column(String(100), nullable=False)
    
    # deprecated columns
    image_source = Column(String(200), nullable=False)
    analysis_database_ip = Column(String(100), nullable=True)
    flat_segmentation_source = Column(String(200), nullable=True)
    pychunkgraph_segmentation_source = Column(String(200), nullable=True)
    annotation_engine_endpoint = Column(String(200), nullable=True)
    synapse_segmentation_source = Column(String(200), nullable=True)
    pychunkedgraph_viewer_source = Column(String(200), nullable=True)
    graphene_source = Column(String(200), nullable=True)
    pychunkedgraph_supervoxel_source = Column(String(200), nullable=True)
    pychunkgraph_endpoint = Column(String(200), nullable=True)

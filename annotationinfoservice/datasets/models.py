from sqlalchemy import Column, Integer, String
from annotationinfoservice.database import Base


class NamedModel(object):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

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
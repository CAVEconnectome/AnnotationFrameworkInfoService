from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from annotationinfoservice.database import Base
from annotationinfoservice.datasets.models import DataSet
engine = create_engine("postgres://postgres:postgres@localhost:5432/postgres")
session = sessionmaker(bind=engine)
db_session = scoped_session(session)

# Adds Query Property to Models - enables `User.query.query_method()`
Base.query = db_session.query_property()

# Create Tables
Base.metadata.create_all(bind=engine)

dataset = DataSet(name="test", flat_segmentation_url="http://test_url")
db_session.add(dataset)
db_session.commit()
print(DataSet.query.all())

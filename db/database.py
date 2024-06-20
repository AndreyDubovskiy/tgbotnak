
from sqlalchemy import create_engine
from db.models.BaseModel import BaseModel

engine = create_engine("sqlite:///mainbase.db", echo=False)

BaseModel.metadata.create_all(engine)



def get_engine():
    return engine
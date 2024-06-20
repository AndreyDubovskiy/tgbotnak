from db.models.BaseModel import BaseModel
from db.models.imports import *

class GroupwordsModel(BaseModel):
    __tablename__ = 'groupwordss'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String())

    words = relationship("WordModel", back_populates="group")


    def __init__(self, name: str):
        self.name = name

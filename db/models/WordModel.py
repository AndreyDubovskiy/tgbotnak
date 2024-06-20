from db.models.BaseModel import BaseModel
from db.models.imports import *

class WordModel(BaseModel):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String())

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groupwordss.id'), nullable=True)
    group = relationship("GroupwordsModel", back_populates="words")


    def __init__(self, name: str):
        self.name = name

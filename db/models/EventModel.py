from db.models.BaseModel import BaseModel
from db.models.imports import *

class EventModel(BaseModel):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True)
    acc_id: Mapped[int] = mapped_column(Integer())
    name_type: Mapped[str] = mapped_column(String())
    tg_id: Mapped[str] = mapped_column(String())
    tg_id_group: Mapped[str] = mapped_column(String())
    time_create = Column(DateTime(timezone=True), server_default=func.now())


    def __init__(self,acc_id:int, name_type: str, tg_id: str, tg_id_group: str):
        self.acc_id = acc_id
        self.name_type = name_type
        self.tg_id = tg_id
        self.tg_id_group = tg_id_group

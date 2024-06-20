from db.models.BaseModel import BaseModel
from db.models.imports import *

class ConfigModel(BaseModel):
    __tablename__ = 'configs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    value: Mapped[str] = mapped_column(String(255), nullable=True)
    group: Mapped[str] = mapped_column(String(255), nullable=True)
    binary_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)


    def __init__(self, name: str, value: str = None, group: str = None, binary_data: bytes = None):
        self.name = name
        self.value = value
        self.group = group
        self.binary_data = binary_data

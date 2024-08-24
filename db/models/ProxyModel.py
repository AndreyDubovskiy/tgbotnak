from db.models.BaseModel import BaseModel
from db.models.imports import *

class ProxyModel(BaseModel):
    __tablename__ = 'proxys'

    id: Mapped[int] = mapped_column(primary_key=True)
    type_proxy: Mapped[int] = mapped_column(Integer())
    ip: Mapped[str] = mapped_column(String(255))
    port: Mapped[int] = mapped_column(Integer())
    login: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)

    accs = relationship("AccModel", back_populates="proxy")


    def __init__(self, type_proxy: int, ip: str, port: int, login: str, password: str):
        self.type_proxy = type_proxy
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password

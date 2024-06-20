from db.models.BaseModel import BaseModel
from db.models.imports import *

class AccModel(BaseModel):
    __tablename__ = 'accs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    session_name: Mapped[str] = mapped_column(String(255))
    api_id: Mapped[str] = mapped_column(String(255))
    api_hash: Mapped[str] = mapped_column(String(255))

    password: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)

    proxy_id: Mapped[int] = mapped_column(Integer, ForeignKey('proxys.id'), nullable=True)
    proxy = relationship("ProxyModel", back_populates="accs")

    def __init__(self, name: str, session_name: str, api_id: str, api_hash: str, phone:str, is_active:bool = False, password:str = None, proxy_id: int = None):
        self.name = name
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.proxy_id = proxy_id
        self.password = password
        self.phone = phone
        self.is_active = is_active

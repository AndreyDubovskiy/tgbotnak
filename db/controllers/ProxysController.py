from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
from db.controllers.TemplateController import Controller
from db.models.ProxyModel import ProxyModel

class ProxysController(Controller):
    def get_all(self):
        with Session(self.engine) as session:
            query = select(ProxyModel)
            query = query.options(joinedload(ProxyModel.accs))
            res: List[ProxyModel] = session.scalars(query).all()
        return res

    def get_by(self, id = None, type_proxy = None, ip = None, port = None):
        with Session(self.engine) as session:
            query = select(ProxyModel)
            if id != None:
                query = query.where(ProxyModel.id == id)
            if type_proxy != None:
                query = query.where(ProxyModel.type_proxy == type_proxy)
            if ip != None:
                query = query.where(ProxyModel.ip == ip)
            if port != None:
                query = query.where(ProxyModel.port == port)
            query = query.options(joinedload(ProxyModel.accs))
            res: List[ProxyModel] = session.scalars(query).all()
        return res

    def create(self, type_proxy: int, ip: str, port: int, login: str, password: str):
        with Session(self.engine) as session:
            tmp = ProxyModel(type_proxy, ip, port, login, password)
            session.add(tmp)
            session.commit()
            session.refresh(tmp)
        return tmp

    def delete(self, id):
        with Session(self.engine) as session:
            query = select(ProxyModel).where(ProxyModel.id == id)
            tmp: ProxyModel = session.scalars(query).first()
            session.delete(tmp)
            session.commit()
        return tmp

    def get_sorted_by_accs_count(self):
        with Session(self.engine) as session:
            subquery = select(
                ProxyModel.id,
                func.count(ProxyModel.accs).label('accs_count')
            ).join(ProxyModel.accs).group_by(ProxyModel.id).subquery()

            query = select(ProxyModel).join(subquery, ProxyModel.id == subquery.c.id).order_by(subquery.c.accs_count.desc())

            res: List[ProxyModel] = session.scalars(query).all()
        return res
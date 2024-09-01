from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
from db.controllers.TemplateController import Controller
from db.models.ProxyModel import ProxyModel
from db.models.AccModel import AccModel

class ProxysController(Controller):
    def get_all(self):
        with Session(self.engine) as session:
            query = select(ProxyModel)
            query = query.options(joinedload(ProxyModel.accs))
            res: List[ProxyModel] = session.scalars(query).unique().all()
        return res

    def get_by(self, id = None, type_proxy = None, ip = None, port = None, limit = None, offset = None):
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
            if offset != None:
                query = query.offset(offset)
            if limit != None:
                query = query.limit(limit)
            query = query.options(joinedload(ProxyModel.accs))
            res: List[ProxyModel] = session.scalars(query).unique().all()
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
            subquery = (
                select(
                    AccModel.proxy_id,
                    func.count(AccModel.id).label('accs_count')
                ).group_by(AccModel.proxy_id)
            ).subquery()

            query = (
                select(ProxyModel)
                .outerjoin(subquery, ProxyModel.id == subquery.c.proxy_id)
                .order_by(subquery.c.accs_count.desc().nullslast())
            )

            res: List[ProxyModel] = session.scalars(query).all()
        return res
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
from db.controllers.TemplateController import Controller
from db.models.AccModel import AccModel

class AccsController(Controller):
    def get_all(self):
        with Session(self.engine) as session:
            query = select(AccModel)
            query = query.options(joinedload(AccModel.proxy))
            res: List[AccModel] = session.scalars(query).all()
        return res

    def get_by(self, id = None, name = None, session_name = None, offset = None, limit = None, is_active = None):
        with Session(self.engine) as session:
            query = select(AccModel)
            if id != None:
                query = query.where(AccModel.id == id)
            if name != None:
                query = query.where(AccModel.name == name)
            if session_name != None:
                query = query.where(AccModel.session_name == session_name)
            if is_active != None:
                query = query.where(AccModel.is_active == is_active)
            if offset != None:
                query = query.offset(offset)
            if limit != None:
                query = query.limit(limit)
            query = query.options(joinedload(AccModel.proxy))
            res: List[AccModel] = session.scalars(query).all()
        return res

    def create(self, name: str, session_name: str, api_id: str, api_hash: str, phone:str, password:str = None, is_active:bool = False, proxy_id: int = None):
        with Session(self.engine) as session:
            tmp = AccModel(name, session_name, api_id, api_hash, phone, is_active, password, proxy_id)
            session.add(tmp)
            session.commit()
        return tmp

    def delete(self, id):
        with Session(self.engine) as session:
            query = select(AccModel).where(AccModel.id == id)
            tmp: AccModel = session.scalars(query).first()
            session.delete(tmp)
            session.commit()
        return tmp
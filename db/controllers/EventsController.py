from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
from db.controllers.TemplateController import Controller
from db.models.EventModel import EventModel

class EventsController(Controller):
    def get_all(self):
        with Session(self.engine) as session:
            query = select(EventModel)
            res: List[EventModel] = session.scalars(query).all()
        return res

    def get_by(self,id = None, acc_id = None, name_type = None, tg_id = None, tg_id_group = None, start_date = None, end_date = None, name_type_value = None):
        with Session(self.engine) as session:
            query = select(EventModel)
            if id != None:
                query = query.where(EventModel.id == id)
            if acc_id != None:
                query = query.where(EventModel.acc_id == acc_id)
            if name_type != None:
                query = query.where(EventModel.name_type == name_type)
            if tg_id != None:
                query = query.where(EventModel.tg_id == tg_id)
            if tg_id_group != None:
                query = query.where(EventModel.tg_id_group == tg_id_group)
            if start_date != None:
                query = query.where(EventModel.time_create >= start_date)
            if end_date != None:
                query = query.where(EventModel.time_create <= end_date)
            if name_type_value != None:
                query = query.where(EventModel.name_type.startswith(name_type_value))
            res: List[EventModel] = session.scalars(query).all()
        return res

    def create(self, acc_id: int, name_type: str, tg_id: str, tg_id_group: str):
        with Session(self.engine) as session:
            tmp = EventModel(acc_id, name_type, tg_id, tg_id_group)
            session.add(tmp)
            session.commit()
            session.refresh(tmp)
        return tmp

    def delete(self, id):
        with Session(self.engine) as session:
            query = select(EventModel).where(EventModel.id == id)
            tmp: EventModel = session.scalars(query).first()
            session.delete(tmp)
            session.commit()
        return tmp
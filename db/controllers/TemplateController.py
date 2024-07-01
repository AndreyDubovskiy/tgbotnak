from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
import db.database as db

class Controller:
    def __init__(self, engine = None):
        self.engine = engine
        if self.engine == None:
            self.engine = db.get_engine()

    def get_all(self, class_model):
        with Session(self.engine) as session:
            query = select(class_model)
            res: List[class_model] = session.scalars(query).all()
        return res

    def get_by(self, class_model, id):
        with Session(self.engine) as session:
            query = select(class_model).where(class_model.id == id)
            res: List[class_model] = session.scalars(query).all()
        return res

    def create(self, class_model):
        with Session(self.engine) as session:
            tmp = class_model()
            session.add(tmp)
            session.commit()
            session.refresh(tmp)
        return tmp

    def delete(self, class_model, id):
        with Session(self.engine) as session:
            query = select(class_model).where(class_model.id == id)
            tmp: class_model = session.scalars(query).first()
            session.delete(tmp)
            session.commit()
        return tmp

    def save(self, obj_model):
        with Session(self.engine) as session:
            session.add(obj_model)
            session.commit()
            session.refresh(obj_model)
        return obj_model

    def save_all(self, obj_models):
        with Session(self.engine) as session:
            session.add_all(obj_models)
            session.commit()
        return obj_models
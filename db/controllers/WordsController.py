from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
from db.controllers.TemplateController import Controller
from db.models.WordModel import WordModel

class WordsController(Controller):
    def get_all(self):
        with Session(self.engine) as session:
            query = select(WordModel)
            query = query.options(joinedload(WordModel.group))
            res: List[WordModel] = session.scalars(query).all()
        return res

    def get_by(self, id = None, name = None, group_id = None):
        with Session(self.engine) as session:
            query = select(WordModel)
            if id != None:
                query = query.where(WordModel.id == id)
            if name != None:
                query = query.where(WordModel.name == name)
            if group_id != None:
                query = query.where(WordModel.group_id == group_id)
            query = query.options(joinedload(WordModel.group))
            res: List[WordModel] = session.scalars(query).all()
        return res

    def create(self, name: str, group):
        with Session(self.engine) as session:
            tmp = WordModel(name)
            tmp.group = group
            session.add(tmp)
            session.commit()
            session.refresh(tmp)
        return tmp

    def delete(self, id):
        with Session(self.engine) as session:
            query = select(WordModel).where(WordModel.id == id)
            tmp: WordModel = session.scalars(query).first()
            session.delete(tmp)
            session.commit()
        return tmp
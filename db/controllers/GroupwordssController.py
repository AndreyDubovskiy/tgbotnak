from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
from db.controllers.TemplateController import Controller
from db.models.GroupwordsModel import GroupwordsModel

class GroupwordssController(Controller):
    def get_all(self):
        with Session(self.engine) as session:
            query = select(GroupwordsModel)
            query = query.options(joinedload(GroupwordsModel.words))
            res: List[GroupwordsModel] = session.scalars(query).all()
        return res

    def get_by(self, id = None, name = None):
        with Session(self.engine) as session:
            query = select(GroupwordsModel)
            if id != None:
                query = query.where(GroupwordsModel.id == id)
            if name != None:
                query = query.where(GroupwordsModel.name == name)
            query = query.options(joinedload(GroupwordsModel.words))
            res: List[GroupwordsModel] = session.scalars(query).all()
        return res

    def create(self, name: str):
        with Session(self.engine) as session:
            tmp = GroupwordsModel(name)
            session.add(tmp)
            session.commit()
        return tmp

    def delete(self, id):
        with Session(self.engine) as session:
            query = select(GroupwordsModel).where(GroupwordsModel.id == id)
            tmp: GroupwordsModel = session.scalars(query).first()
            session.delete(tmp)
            session.commit()
        return tmp
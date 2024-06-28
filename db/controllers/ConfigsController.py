from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import joinedload
from db.controllers.TemplateController import Controller
from db.models.ConfigModel import ConfigModel

class ConfigsController(Controller):
    def get_all(self):
        with Session(self.engine) as session:
            query = select(ConfigModel)
            res: List[ConfigModel] = session.scalars(query).all()
        return res

    def get_by(self, id = None, name = None, group = None, value = None):
        with Session(self.engine) as session:
            query = select(ConfigModel)
            if id != None:
                query = query.where(ConfigModel.id == id)
            if name != None:
                query = query.where(ConfigModel.name == name)
            if group != None:
                query = query.where(ConfigModel.group == group)
            if value != None:
                query = query.where(ConfigModel.value == value)
            res: List[ConfigModel] = session.scalars(query).all()
        return res

    def create(self, name: str, value: str = None, group: str = None, binary_data: bytes = None):
        with Session(self.engine) as session:
            tmp = ConfigModel(name, value, group, binary_data)
            session.add(tmp)
            session.commit()
            session.refresh(tmp)
        return tmp

    def delete(self, id):
        with Session(self.engine) as session:
            query = select(ConfigModel).where(ConfigModel.id == id)
            tmp: ConfigModel = session.scalars(query).first()
            session.delete(tmp)
            session.commit()
        return tmp

    def set_config(self, name: str, value: str = None, group: str = None, binary_data: bytes = None):
        tmp = self.get_by(name=name)
        if len(tmp) == 0:
            self.create(name, value, group, binary_data)
        else:
            tmp = tmp[0]
            if value != None:
                tmp.value = value
            if group != None:
                tmp.group = group
            if binary_data != None:
                tmp.binary_data = binary_data
            self.save(tmp)

    def get_config(self, name: str):
        tmp = self.get_by(name=name)
        if len(tmp) == 0:
            tmp = self.create(name)
            return tmp
        else:
            tmp = tmp[0]
            return tmp
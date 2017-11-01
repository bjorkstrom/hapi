from sqlalchemy import Column, Integer, String
from database import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    # dictionary key names used for serialization
    NAME = "name"
    DESC = "description"

    def as_dict(self):
        return dict(name=self.name,
                    description=self.description)

    def update(self, new_vals):
        if Model.NAME in new_vals:
            self.name = new_vals[Model.NAME]

        if Model.DESC in new_vals:
            self.description = new_vals[Model.DESC]

    @staticmethod
    def from_dict(data):
        return Model(name=Model.NAME,
                     description=Model.DESC)

    @staticmethod
    def get(id):
        return Model.query.filter(Model.id == id).first()

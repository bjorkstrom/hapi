from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy import orm
from database import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    default_position_id = Column(Integer, ForeignKey("swerefPos.id"))
    default_position = orm.relationship("SwerefPos")

    # dictionary key names used for serialization
    NAME = "name"
    DESC = "description"

    def as_dict(self):
        d = dict(name=self.name, description=self.description)

        if self.default_position is not None:
            d["defaultPosition"] = dict(
                sweref99=self.default_position.as_dict())

        return d

    def update(self, new_vals):
        if Model.NAME in new_vals:
            self.name = new_vals[Model.NAME]

        if Model.DESC in new_vals:
            self.description = new_vals[Model.DESC]

    @staticmethod
    def from_dict(data):
        args = dict(name=data[Model.NAME],
                     description=data[Model.DESC])

        # add default position of specified
        if "defaultPosition" in data:
            args["default_position"] = \
                SwerefPos.from_dict(data["defaultPosition"]["sweref99"])

        return Model(**args)

    @staticmethod
    def get(id):
        return Model.query.filter(Model.id == id).first()


class SwerefPos(Base):
    __tablename__ = "swerefPos"

    id = Column(Integer, primary_key=True)
    projection = Column(String)
    x = Column(Numeric)
    y = Column(Numeric)
    z = Column(Numeric)
    roll = Column(Numeric)
    pitch = Column(Numeric)
    yaw = Column(Numeric)

    @staticmethod
    def from_dict(data):
        return SwerefPos(
            projection = data["projection"],
            x = data["x"],
            y = data["y"],
            z = data["z"],
            roll = data.get("roll", 0),
            pitch = data.get("pitch", 0),
            yaw = data.get("yaw", 0))

    def as_dict(self):
        return dict(
            projection=self.projection,
            x=self.x,
            y=self.y,
            z=self.z,
            roll=self.roll,
            pitch=self.pitch,
            yaw=self.yaw)

        return d

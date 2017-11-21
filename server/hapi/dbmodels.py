import enum

from hapi.database import Base
from sqlalchemy import Column, Integer, String, Numeric, Boolean
from sqlalchemy import Enum, ForeignKey, orm

_ImportStat = enum.Enum("ImportStatus",
                        "processing done failed")

#
# common dictionary key names used for serialization
#
MODEL = "model"
NAME = "name"
DESC = "description"
HIDDEN = "hidden"
POSITION = "position"
SWRREF99 = "sweref99"
DEF_POS = "defaultPosition"


class ModelNotFound(Exception):
    def __init__(self, modelId):
        self.modelId = modelId


class Device(Base):
    __tablename__ = "devices"

    serialNo = Column(String, primary_key=True)

    model_instances = orm.relationship("ModelInstance")

    @staticmethod
    def get(serialNo):
        return Device.query.filter(Device.serialNo == serialNo).first()


def _add_if_not_none(d, name, val):
    if val is None:
        # don't add
        return

    d[name] = val


class ModelInstance(Base):
    __tablename__ = "model_instances"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    hidden = Column(Boolean)

    _model_id = Column("model", Integer, ForeignKey("models.id"))
    model = orm.relationship("Model")

    _position_id = Column("position", Integer, ForeignKey("swerefPos.id"))
    position = orm.relationship("SwerefPos")

    _device = Column("device", String, ForeignKey("devices.serialNo"))
    device = orm.relationship("Device")

    def as_dict(self):
        d = dict(model=str(self.model.id),
                 hidden=self.hidden)

        _add_if_not_none(d, NAME, self.name)
        _add_if_not_none(d, DESC, self.description)

        if self.position is not None:
            d[POSITION] = dict(sweref99=self.position.as_dict())

        return d

    @staticmethod
    def from_dict(device, data):
        def _get_position():
            if POSITION in data:
                return SwerefPos.from_dict(data[POSITION][SWRREF99])

            # no instance position specified,
            # use model's default position if available
            if mod.default_position is not None:
                return mod.default_position.copy()

            # position not known for this instance at this time
            return None

        modId = data[MODEL]
        mod = Model.get(modId)
        if mod is None:
            raise ModelNotFound(modId)

        args = dict(
            name=data.get(NAME),
            description=data.get(DESC),
            hidden=data.get(HIDDEN, False),
            model=mod,
            device=device,
            position=_get_position(),
        )

        return ModelInstance(**args)


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    import_status = Column(Enum(_ImportStat))

    default_position_id = Column(Integer, ForeignKey("swerefPos.id"))
    default_position = orm.relationship("SwerefPos")

    def as_dict(self):
        d = dict(importStatus=self.import_status.name)

        _add_if_not_none(d, "name", self.name)
        _add_if_not_none(d, "description", self.description)

        if self.default_position is not None:
            d["defaultPosition"] = dict(
                sweref99=self.default_position.as_dict())

        return d

    def update(self, new_vals):
        if NAME in new_vals:
            self.name = new_vals[NAME]

        if DESC in new_vals:
            self.description = new_vals[DESC]

    @staticmethod
    def from_dict(data):
        args = dict(name=data.get(NAME),
                    description=data.get(DESC),
                    import_status=_ImportStat.processing)

        # add default position of specified
        if DEF_POS in data:
            args["default_position"] = \
                SwerefPos.from_dict(data[DEF_POS][SWRREF99])

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

    def copy(self):
        return SwerefPos(
            projection=self.projection,
            x=self.x,
            y=self.y,
            z=self.z,
            roll=self.roll,
            pitch=self.pitch,
            yaw=self.yaw)

    @staticmethod
    def from_dict(data):
        return SwerefPos(
            projection=data["projection"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            roll=data.get("roll", 0),
            pitch=data.get("pitch", 0),
            yaw=data.get("yaw", 0))

    def as_dict(self):
        return dict(
            projection=self.projection,
            x=self.x,
            y=self.y,
            z=self.z,
            roll=self.roll,
            pitch=self.pitch,
            yaw=self.yaw)

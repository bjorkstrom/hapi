import enum
import time
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

    SERIAL_NO_LEN = 16

    serialNo = Column(String(SERIAL_NO_LEN), primary_key=True)
    model_instances = orm.relationship("ModelInstance")

    subscriptions = orm.relationship('Subscription',
                                     backref='sub',
                                     lazy='dynamic')

    def as_dict(self):
        return dict(serialNo=self.serialNo)

    @staticmethod
    def all():
        return Device.query.all()

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
    name = Column(String(128))
    description = Column(String(256))
    hidden = Column(Boolean)

    _model_id = Column("model", ForeignKey("models.id"))
    model = orm.relationship("Model")

    _position_id = Column("position", ForeignKey("swerefPos.id"))
    position = orm.relationship("SwerefPos")

    _device = Column("device", ForeignKey("devices.serialNo"))
    device = orm.relationship("Device")

    def as_dict(self):
        d = dict(model=str(self.model.id),
                 hidden=self.hidden)

        _add_if_not_none(d, NAME, self.name)
        _add_if_not_none(d, DESC, self.description)

        if self.position is not None:
            d[POSITION] = dict(sweref99=self.position.as_dict())

        return d

    def delete(self, session):
        """
        delete this model instance and it's position, if any,
        in the specified session
        """
        if self.position is not None:
            session.delete(self.position)
        session.delete(self)

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

        return ModelInstance(
            name=data.get(NAME),
            description=data.get(DESC),
            hidden=data.get(HIDDEN, False),
            model=mod,
            device=device,
            position=_get_position(),
        )


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    description = Column(String(256))
    import_status = Column(Enum(_ImportStat))

    default_position_id = Column(ForeignKey("swerefPos.id"))
    default_position = orm.relationship("SwerefPos")

    instances = orm.relationship("ModelInstance")

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

    def delete(self, session):
        """
        delete this model and it's default position, if any,
        in the specified session
        """
        if self.default_position is not None:
            # delete default position, if it was specified
            session.delete(self.default_position)
        session.delete(self)

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
    def all():
        return Model.query.all()

    @staticmethod
    def get(id):
        return Model.query.filter(Model.id == id).first()


class SwerefPos(Base):
    __tablename__ = "swerefPos"

    # 15 max total digit include decimals
    # 5 max digits after the decimal point
    POS_PRECISION = "15,5"

    id = Column(Integer, primary_key=True)
    projection = Column(String(8))
    x = Column(Numeric(precision=POS_PRECISION))
    y = Column(Numeric(precision=POS_PRECISION))
    z = Column(Numeric(precision=POS_PRECISION))
    roll = Column(Numeric(precision=POS_PRECISION))
    pitch = Column(Numeric(precision=POS_PRECISION))
    yaw = Column(Numeric(precision=POS_PRECISION))

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


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    expiration = Column(Integer)

    _device = Column("device", ForeignKey("devices.serialNo"))
    device = orm.relationship("Device")

    _restEndpoint = Column("restEndpoint",
                           ForeignKey("restEndpoints.id", ondelete="CASCADE"))
    restEndpoint = orm.relationship("RestEndpoint")
    topics = orm.relationship('EventTopics',
                              backref='owner',
                              lazy='dynamic',
                              passive_deletes=True)

    @staticmethod
    def from_dict(device, data):
        def _get_restEndpoint():
            return RestEndpoint.from_dict(data["destination"]["restEndpoint"])

        def _get_topics():
            topics = []
            for topic_dict in data["eventFilters"]:
                topics.append(EventTopics.from_dict(topic_dict))

            return topics

        return Subscription(
            expiration=Subscription.get_Expiration(data["duration"]),
            restEndpoint=_get_restEndpoint(),
            device=device,
            topics=_get_topics()
        )

    @staticmethod
    def get(subId):
        return Subscription.query.filter(Subscription.id == subId).first()

    @staticmethod
    def get_Expiration(duration):
        epoch_time = time.time()
        return duration + int(epoch_time)


class RestEndpoint(Base):
    __tablename__ = "restEndpoints"

    id = Column(Integer, primary_key=True)
    url = Column(String(256))
    method = Column(String(16))
    # httpheaders: a virtual column to being as a reference
    httpheaders = orm.relationship('HttpHeader',
                                   backref='owner',
                                   lazy='dynamic',
                                   passive_deletes=True)

    @staticmethod
    def from_dict(data):
        def _get_headers():
            headers = []
            for header_dict in data["headers"]:
                headers.append(HttpHeader.from_dict(header_dict))

            return headers

        args = dict(url=data["URL"],
                    method=data["method"])

        if "headers" in data:
            args["httpheaders"] = _get_headers()

        return RestEndpoint(**args)

    @staticmethod
    def get(restID):
        return RestEndpoint.query.filter(RestEndpoint.id == restID).first()


class HttpHeader(Base):
    __tablename__ = "httpHeaders"

    name = Column(String(64), primary_key=True)
    value = Column(String(256))
    _restEndpoints = Column("restEndpoint",
                            ForeignKey("restEndpoints.id",
                                       ondelete="CASCADE"),
                            primary_key=True)
    restEndpoint = orm.relationship("RestEndpoint")

    @staticmethod
    def from_dict(data):
        return HttpHeader(name=data["name"],
                          value=data["value"])


class EventTopics(Base):
    __tablename__ = "topicEvents"

    topic = Column(String(64), primary_key=True)
    _subscription = Column("subscription",
                           ForeignKey("subscriptions.id",
                                      ondelete="CASCADE"),
                           primary_key=True)
    subscription = orm.relationship("Subscription")

    @staticmethod
    def from_dict(data):
        return EventTopics(topic=data["topic"])

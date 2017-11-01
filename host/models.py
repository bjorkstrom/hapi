import bson
import flask
from dbmodels import Model
import database


def _parse_model_bson(bson_bytes):
    return bson.loads(bson_bytes)


def new(model):
    mod = Model.from_dict(_parse_model_bson(model))
    database.db_session.add(mod)
    database.db_session.commit()

    return dict(model=mod.id)


def update(modelID, body):
    mod = Model.get(modelID)
    mod.update(body)
    database.db_session.commit()

    return flask.Response(status=204)


def get(modelID):
    return Model.get(modelID).as_dict()


def delete(modelID):
    mod = Model.get(modelID)
    database.db_session.delete(mod)
    database.db_session.commit()

    return flask.Response(status=204)

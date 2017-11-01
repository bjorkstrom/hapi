import bson
import flask
from dbmodels import Model
import database


def _parse_model_bson(bson_bytes):
    return bson.loads(bson_bytes)


def _model_not_found_resp(modelID):
    msg = "No model with id '%s' exists" % modelID
    return dict(message=msg), 404

def new(model):
    mod = Model.from_dict(_parse_model_bson(model))
    database.db_session.add(mod)
    database.db_session.commit()

    return dict(model=mod.id)


def update(modelID, body):
    mod = Model.get(modelID)
    if mod is None:
        return _model_not_found_resp(modelID)

    mod.update(body)
    database.db_session.commit()

    return flask.Response(status=204)


def get(modelID):
    mod = Model.get(modelID)
    if mod is None:
        return _model_not_found_resp(modelID)

    return Model.get(modelID).as_dict()


def delete(modelID):
    mod = Model.get(modelID)
    if mod is None:
        return _model_not_found_resp(modelID)

    database.db_session.delete(mod)
    database.db_session.commit()

    return flask.Response(status=204)

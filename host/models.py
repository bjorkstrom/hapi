import bson
import flask
from dbmodels import Model
import database


class ParseException(Exception):
    pass


def _invalid_model_resp(ex):
    return dict(message=str(ex)), 400


def _model_not_found_resp(modelID):
    msg = "No model with id '%s' exists" % modelID
    return dict(message=msg), 404


def _parse_model_bson(bson_bytes):
    try:
        mod_dict = bson.loads(bson_bytes)
    except Exception:
        raise ParseException("malformed bson data")

    return mod_dict


def new(model):
    try:
        mod = Model.from_dict(_parse_model_bson(model))
    except ParseException as e:
        return _invalid_model_resp(e)

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

import flask
from dbmodels import Model
import database
import new_model


def _invalid_model_resp(ex):
    return dict(message=str(ex)), 400


def _model_not_found_resp(modelID):
    msg = "No model with id '%s' exists" % modelID
    return dict(message=msg), 404


def new(model):
    try:
        modID = new_model.add_model(model)
    except new_model.InvalidModel as e:
        return _invalid_model_resp(e)

    return dict(model=modID)


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

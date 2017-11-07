import database
import flask
from dbmodels import Model
from . import new_model


def _invalid_model_resp(ex):
    return dict(message=str(ex)), 400


def _model_not_found_resp(modelID):
    msg = "No model with id '%s' exists" % modelID
    return dict(message=msg), 404


#
# POST /models/new
#
def post(modelFile, model):
    print("at new_model")
    try:
        modID = new_model.add_model(modelFile, model)
    except new_model.InvalidModel as e:
        return _invalid_model_resp(e)

    return dict(model=str(modID)), 201

#
# PUT /models/{modelId}
#
def put(modelId, modelUpdate):
    mod = Model.get(modelId)
    if mod is None:
        return _model_not_found_resp(modelId)

    mod.update(modelUpdate)
    database.db_session.commit()

    return flask.Response(status=204)


#
# GET /models/{modelId}
#
def get(modelId):
    mod = Model.get(modelId)
    if mod is None:
        return _model_not_found_resp(modelId)

    return mod.as_dict()

#
# DELETE /models/{modelId}
#
def delete(modelId):
    mod = Model.get(modelId)
    if mod is None:
        return _model_not_found_resp(modelId)

    database.db_session.delete(mod)
    database.db_session.commit()

    return flask.Response(status=204)


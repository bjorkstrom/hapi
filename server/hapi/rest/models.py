import flask
from flask import request
from hapi.dbmodels import Model, User
from hapi import database

from . import new_model, util


def _invalid_model_resp(ex):
    return dict(message=str(ex)), 400


def _model_instantiated_resp():
    # TODO: include a list of device's serial numbers
    # TODO: where model is instantiated in the error reply
    return dict(message="model instantiated on some device(s), "
                        "unable to delete"), 400


#
# POST /models/new
#
def new(modelFile, model):
    # figure out current user ID
    usr_id = User.get(request.authorization.username).id

    try:
        modID = new_model.add_model(modelFile, model, usr_id)
    except new_model.InvalidModel as e:
        return _invalid_model_resp(e)

    return dict(model=str(modID)), 201


#
# GET /models
#
def search():
    models = [dict(model=str(m.id)) for m in Model.all()]
    return dict(models=models)


#
# PUT /models/{modelId}
#
def put(modelId, modelUpdate):
    mod = Model.get(modelId)
    if mod is None:
        return util.model_not_found_resp(modelId)

    mod.update(modelUpdate)
    database.db_session.commit()

    return flask.Response(status=204)


#
# GET /models/{modelId}
#
def get(modelId):
    mod = Model.get(modelId)
    if mod is None:
        return util.model_not_found_resp(modelId)

    return mod.as_dict()


#
# DELETE /models/{modelId}
#
def delete(modelId):
    mod = Model.get(modelId)
    if mod is None:
        return util.model_not_found_resp(modelId)

    if len(mod.instances) > 0:
        # model is instantiated on some device
        return _model_instantiated_resp()

    session = database.db_session
    mod.delete(session)
    session.commit()

    return flask.Response(status=204)

import flask
from sqlalchemy import exc
from hapi.dbmodels import Model
from hapi import database

from . import new_model, util


def _invalid_model_resp(ex):
    return dict(message=str(ex)), 400


def _model_instantiated_resp():
    return dict(message="model instantiated on some device(s), "
                        "unable to delete"), 400


#
# POST /models/new
#
def post(modelFile, model):
    try:
        modID = new_model.add_model(modelFile, model)
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

    session = database.db_session
    mod.delete(session)

    try:
        session.commit()
    except exc.IntegrityError as e:
        # we kind of assume, or rather, hope
        # that the integrity error is triggered by the
        # foreign key constrain violation, because there
        # are some instances of this model,
        # but we can't really be sure, as the exception is not
        # that explicit why it's raised
        # TODO: include a list of device's serial numbers
        # TODO: where model is instantiated in the error reply
        return _model_instantiated_resp()

    return flask.Response(status=204)

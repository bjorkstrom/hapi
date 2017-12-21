import flask
from hapi.dbmodels import Model
from hapi import database
from hapi import auth

from . import new_model, util, aws


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
@auth.user
def new(modelFile, model):
    try:
        modID = new_model.add_model(modelFile, model,
                                    util.get_user())
    except new_model.InvalidModel as e:
        return _invalid_model_resp(e)

    return dict(model=str(modID)), 201


#
# GET /models
#
@auth.user
def search():
    models = [dict(model=str(m.id)) for m in Model.all()]
    return dict(models=models)


#
# PUT /models/{modelId}
#
@auth.user
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
@auth.user
def get(modelId):
    mod = Model.get(modelId)
    if mod is None:
        return util.model_not_found_resp(modelId)

    return mod.as_dict()


#
# DELETE /models/{modelId}
#
@auth.user
def delete(modelId):
    mod = Model.get(modelId)
    if mod is None:
        return util.model_not_found_resp(modelId)

    if len(mod.instances) > 0:
        # model is instantiated on some device
        return _model_instantiated_resp()

    aws.delete_models_s3_objs(mod.id,
                              util.get_user_id())

    session = database.db_session
    mod.delete(session)
    session.commit()

    return flask.Response(status=204)

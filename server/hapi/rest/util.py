from hapi.dbmodels import User, ModelNotFound, NoModelInstancePosition
from flask import request


def model_instance_error_resp(ex):
    if isinstance(ex, ModelNotFound):
        return model_not_found_resp(ex.modelId)

    if isinstance(ex, NoModelInstancePosition):
        msg = "no position specified for model '%s' " \
              "and no implicit position is known for that model" % ex.modelId
        return dict(message=msg), 400

    assert False, "unexpected exception type"


def model_not_found_resp(modelId):
    msg = "no model with id '%s' exists" % modelId
    return dict(message=msg), 404


def device_not_found_resp(serialNo):
    msg = "no device with serial number '%s' exists" % serialNo
    return dict(message=msg), 404


def get_user():
    # figure out current user ID
    return User.get(request.authorization.username)


def get_user_id():
    # figure out current user ID
    return get_user().id

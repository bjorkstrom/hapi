from hapi.dbmodels import User
from flask import request


def model_not_found_resp(modelId):
    msg = "no model with id '%s' exists" % modelId
    return dict(message=msg), 404


def device_not_found_resp(serialNo):
    msg = "no device with serial number '%s' exists" % serialNo
    return dict(message=msg), 404


def get_user_id():
    # figure out current user ID
    return User.get(request.authorization.username).id

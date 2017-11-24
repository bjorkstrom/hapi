import flask
from hapi.dbmodels import Device, ModelInstance, ModelNotFound
from hapi import database

from . import util


def _device_not_found_resp(serialNo):
    msg = "no device with serial number '%s' exists" % serialNo
    return dict(message=msg), 404


#
# POST /device/{serialNo}/models
#
def post(serialNo, modelInstances):
    device = Device.get(serialNo)
    if device is None:
        return _device_not_found_resp(serialNo)

    session = database.db_session

    # delete old model instances
    for mod_inst in device.model_instances:
        session.delete(mod_inst)

    try:
        for mod_inst in modelInstances["modelInstances"]:
            session.add(ModelInstance.from_dict(device, mod_inst))
    except ModelNotFound as e:
        session.expunge_all()  # don't write any changes to the database
        return util.model_not_found_resp(e.modelId)

    session.commit()

    return flask.Response(status=204)


#
# GET /device/{serialNo}/models
#
def get(serialNo):
    device = Device.get(serialNo)
    if device is None:
        return _device_not_found_resp(serialNo)

    instances = []
    for mod_inst in device.model_instances:
        instances.append(mod_inst.as_dict())

    return dict(modelInstances=instances)

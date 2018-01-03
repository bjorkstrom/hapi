import flask
from hapi.dbmodels import Device, ModelInstance, ModelException
from hapi import database
from hapi import auth

from . import util


#
# POST /device/{serialNo}/models
#
@auth.allow(auth.user)
def post(serialNo, modelInstances):
    device = Device.get(serialNo)
    if device is None:
        return util.device_not_found_resp(serialNo)

    session = database.db_session

    # delete old model instances
    for mod_inst in device.model_instances:
        mod_inst.delete(session)

    try:
        for mod_inst in modelInstances["modelInstances"]:
            session.add(ModelInstance.from_dict(device, mod_inst))
    except ModelException as e:
        session.expunge_all()  # don't write any changes to the database
        return util.model_instance_error_resp(e)

    session.commit()

    return flask.Response(status=204)


#
# GET /device/{serialNo}/models
#
@auth.allow(auth.user, auth.device)
def get(serialNo):
    # TODO we should only give access to device's own models,
    # right now device can access any other device's models
    device = Device.get(serialNo)
    if device is None:
        return util.device_not_found_resp(serialNo)

    instances = []
    for mod_inst in device.model_instances:
        instances.append(mod_inst.as_dict())

    return dict(modelInstances=instances)

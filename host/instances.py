import flask
import database
from dbmodels import Device, ModelInstance


def _device_not_found_resp(serialNo):
    msg = "no device with serial number '%s' exists" % serialNo
    return dict(message=msg), 404


def set(deviceSerialNo, modelInstances):
    device = Device.get(deviceSerialNo)
    if device is None:
        return _device_not_found_resp(deviceSerialNo)

    session = database.db_session

    # delete old model instances
    for mod_inst in device.model_instances:
        session.delete(mod_inst)

    for mod_inst in modelInstances["modelInstances"]:
        session.add(ModelInstance.from_dict(device, mod_inst))

    session.commit()

    return flask.Response(status=204)


def get(deviceSerialNo):
    device = Device.get(deviceSerialNo)
    if device is None:
        return _device_not_found_resp(deviceSerialNo)

    instances = []
    for mod_inst in device.model_instances:
        instances.append(mod_inst.as_dict())

    return dict(modelInstances=instances)
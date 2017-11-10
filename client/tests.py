#!/usr/bin/env python

from bravado.client import SwaggerClient
from bravado.exception import HTTPBadRequest, HTTPNotFound
import json

client = SwaggerClient.from_url("http://localhost:9090/v1/swagger.json")

#from bravado.requests_client import RequestsClient
#http_client = RequestsClient()
#http_client.set_basic_auth(
#    "ncc.brab.ws",
#    "root", "????"
#)

#client = SwaggerClient.from_url("https://ncc.brab.ws/v1/swagger.json",
#                                http_client=http_client)

#
# Create new model
#
mod_dict = {
        "name": "my model",
        "description": "my new model",
        "defaultPosition": {
            "sweref99": {
                "projection": "18 00",
                "x": 6175471.9873,
                "y": 300000.1234,
                "z": 68.0223,
            },
        },
    }
res = client.models.post_models_new(modelFile="dummy_data",
                                    # modelFile=("myfile", "dummy_data"),
                                    model=json.dumps(mod_dict)).result()
modelId = res["model"]

#
# Get created model
#
res = client.models.get_models_modelId(modelId=modelId).result()
assert res.name == "my model"
assert res.description == "my new model"

#
# Update model
#
client.models.put_models_modelId(
    modelId=modelId,
    modelUpdate=dict(name="new name",
                     description="new desc")).result()

#
# Get updated model
#
res = client.models.get_models_modelId(modelId=modelId).result()
assert res.name == "new name"
assert res.description == "new desc"

#
# Create model instances
#
ModelInstances = client.get_model("ModelInstances")
ModelInstance = client.get_model("ModelInstance")

mod_insts = ModelInstances(modelInstances=[
    ModelInstance(name="inst1",
                  model=modelId),
    ModelInstance(name="inst2",
                  model=modelId),
])
client.device.post_device_serialNo_models(
    serialNo="A0", modelInstances=mod_insts).result()

#
# Get model instances
#
res = client.device.get_device_serialNo_models(serialNo="A0").result()
assert len(res.modelInstances) == 2
for mod_inst in res.modelInstances:
    assert mod_inst.model == modelId
    assert mod_inst.name.startswith("inst")

#
# Delete model instances (by setting an empty set)
#
mod_insts = ModelInstances(modelInstances=[])
client.device.post_device_serialNo_models(
    serialNo="A0", modelInstances=mod_insts).result()

#
# Delete model
#
res = client.models.delete_models_modelId(modelId=modelId).result()

#
# Check that we get 404 error when deleting non-existent model
#
try:
    client.models.delete_models_modelId(modelId=modelId).result()
except HTTPNotFound as e:
    err_msg = e.swagger_result.message
    assert err_msg == ("no model with id '%s' exists" % modelId)
else:
    assert False, "NO EXCEPTION"

#
# Check that invalid model description creates
# proper error response
#
try:
    invalid_dict = dict(name=3) # name of wrong type
    client.models.post_models_new(
        modelFile="dummy_data",
        model=json.dumps(invalid_dict)).result()
except HTTPBadRequest as e:
    err_msg = e.swagger_result.message
    assert err_msg.startswith("invalid model description: 3 is not of type 'string'")
else:
    assert False, "NO EXCEPTION"

#
# Try to set model instances on a device that does not exist
#
try:
    client.device.post_device_serialNo_models(
        serialNo="NO_SUCH_DEVICE",
        modelInstances=ModelInstances(modelInstances=[])).result()
except HTTPNotFound as e:
    err_msg = e.swagger_result.message
    assert err_msg.startswith("no device")
else:
    assert False, "NO EXCEPTION"

#
# Try to use non-existing model ID when creating instances
#
try:
    mod_insts = ModelInstances(modelInstances=[
        ModelInstance(name="inst1",
                      model=modelId)])

    client.device.post_device_serialNo_models(
        serialNo="A0", modelInstances=mod_insts).result()
except HTTPNotFound as e:
    err_msg = e.swagger_result.message
    assert err_msg.startswith("no model with id")
else:
    assert False, "NO EXCEPTION"

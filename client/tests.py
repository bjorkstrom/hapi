#!/usr/bin/env python

from bravado.client import SwaggerClient
from bravado.exception import HTTPBadRequest, HTTPNotFound
import json

client = SwaggerClient.from_url("http://localhost:9090/v1/swagger.json")

#
# Create new model
#
mod_dict = dict(name="myModel")
res = client.models.models_new(modelFile="dummy_data",
                               # modelFile=("myfile", "dummy_data"),
                               model=json.dumps(mod_dict)).result()
modelId = res["model"]

#
# Get created model
#
res = client.models.models_get(modelId=modelId).result()
assert res.name == "myModel"
assert res.description is None

#
# Update model
#
client.models.models_update(modelId=modelId,
                            modelUpdate=dict(name="new name",
                                             description="new desc")).result()

#
# Get updated model
#
res = client.models.models_get(modelId=modelId).result()
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
client.device.instances_set(deviceSerialNo="A0", modelInstances=mod_insts).result()

#
# Get model instances
#
res = client.device.instances_get(deviceSerialNo="A0").result()
assert len(res.modelInstances) == 2
for mod_inst in res.modelInstances:
    assert mod_inst.model == modelId
    assert mod_inst.name.startswith("inst")

#
# Delete model instances (by setting an empty set)
#
mod_insts = ModelInstances(modelInstances=[])
client.device.instances_set(deviceSerialNo="A0", modelInstances=mod_insts).result()

#
# Delete model
#
res = client.models.models_delete(modelId=modelId).result()

#
# Check that we get 404 error when deleting non-existent model
#
try:
    client.models.models_delete(modelId=modelId).result()
except HTTPNotFound as e:
    err_msg = e.swagger_result.message
    assert err_msg == ("No model with id '%s' exists" % modelId)
else:
    assert False, "NO EXCEPTION"

#
# Check that invalid model description creates
# proper error response
#
try:
    invalid_dict = dict(name=3) # name of wrong type
    client.models.models_new(modelFile="dummy_data",
                             model=json.dumps(invalid_dict)).result()
except HTTPBadRequest as e:
    err_msg = e.swagger_result.message
    assert err_msg.startswith("invalid model description: 3 is not of type 'string'")
else:
    assert False, "NO EXCEPTION"

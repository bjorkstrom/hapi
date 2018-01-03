from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
import requests
import json
import pprint


def position():
    return dict(
        sweref99=dict(
            projection="13 30",
            x=6175471.9873,
            y=100001.1234,
            z=68.0223,
            yaw=1.1,
            pitch=2.2,
            roll=3.3))

def upload_model_body(filename):
    body = {
        "name": filename,
        "description": "my pretty model",
        "placement" : "global",
        # "defaultPosition": {
        #     "sweref99": {
        #         "projection": "18 00",
        #         "x": 6175471.9873,
        #         "y": 300000.1234,
        #         "z": 68.0223,
        #     },
        # },
    }
    return json.dumps(body)


def model_instance_dict(modelId):
    return dict(
        model=modelId,
        hidden=False,
#        position=position(),
    )


def print_resp(r):
    content_type = r.headers.get("content-type")

    if content_type in [
        "application/json",
        "application/problem+json",
    ]:
        pprint.pprint(r.status_code)
        pprint.pprint(r.json())
    else:
        print(r.status_code)

def get_swagger_client(url, swagger_url, uname, passwd):
    # split on :// to get host name from the url
    # split on ':' to chop off potentional port number
    host = url.split("://")[1].split(":")[0]

    http_client = RequestsClient()
    http_client.set_basic_auth(host, uname, passwd)

    return SwaggerClient.from_url(swagger_url, http_client=http_client)


class HagringCloud:
    def __init__(self, url, port=None, uname=None, passwd=None):
        port = "" if port is None else ":" + str(port)
        self.root_url = "%s/v1" % url
        swagger_url = "%s/swagger.json" % self.root_url
        self.client = get_swagger_client(url, swagger_url, uname, passwd)

        self.ModelInstance = self.client.get_model("ModelInstance")
        self.ModelInstances = self.client.get_model("ModelInstances")




    def newModel(self, filename):
        with open(filename, "rb") as f:
            r = self.client.models.post_models_new(
                modelFile=(filename, f.read()),
                #modelFile=f.read(),
                model=upload_model_body(filename)).result()

        print(r)

    def updateModel(self, id, name, desc):
        url = "%s/models/%s" % (self.root_url, id)
        r = requests.put(url,
                         json=dict(name=name, description=desc))
        print_resp(r)

    def deleteModel(self, id):
        self.client.models.delete_models_modelId(modelId=id).result()

    def getModel(self, id):
        url = "%s/models/%s" % (self.root_url, id)
        r = requests.get(url)
        print(r.status_code, r.json())

    def setModelInstances(self, device_serno, instances):
        mis = [self.ModelInstance(model=mid) for mid in instances]
        mis = self.ModelInstances(modelInstances=mis)

        r = self.client.device.post_device_serialNo_models(serialNo="A0", modelInstances=mis).result()
        print(r)

    def getModelInstances(self, device_serno):
        url = "%s/device/%s/models" % (self.root_url, device_serno)
        r = requests.get(url)
        print_resp(r)

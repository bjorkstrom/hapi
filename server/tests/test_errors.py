import unittest
import json
import utils
from utils import Client, ModelInstances, ModelInstance
from bravado.exception import HTTPBadRequest, HTTPNotFound


class TestNotFoundResp(unittest.TestCase, utils.ErrorReqMixin):

    def test_get_nonexistent_model(self):

        with self.assertRaises(HTTPNotFound) as cm:
            Client.models.get_models_modelId(modelId="XXX").result()

        self._assert_error_msg(cm.exception, "no model with id 'XXX' exists")

    def test_put_nonexistent_model(self):
        with self.assertRaises(HTTPNotFound) as cm:
            Client.models.put_models_modelId(modelId="ZZZ",
                                             modelUpdate=dict()).result()

        self._assert_error_msg(cm.exception, "no model with id 'ZZZ' exists")

    def test_delete_nonexistent_model(self):
        with self.assertRaises(HTTPNotFound) as cm:
            Client.models.delete_models_modelId(modelId="ABC").result()

        self._assert_error_msg(cm.exception, "no model with id 'ABC' exists")

    def test_get_nonexistent_dev_instances(self):
        with self.assertRaises(HTTPNotFound) as cm:
            Client.device.get_device_serialNo_models(serialNo="XXX").result()

        self._assert_error_msg(cm.exception,
                               "no device with serial number 'XXX' exists")

    def test_set_nonexistent_dev_instances(self):
        """
        test setting model instances on a non-existing device
        """
        with self.assertRaises(HTTPNotFound) as cm:
            Client.device.post_device_serialNo_models(
                serialNo="UK",
                modelInstances=ModelInstances(modelInstances=[])).result()

        self._assert_error_msg(cm.exception,
                               "no device with serial number 'UK' exists")

    def test_set_instance_nonexistent_model_id(self):
        mod_insts = ModelInstances(
            modelInstances=[ModelInstance(name="inst1", model="XYZ")])

        with self.assertRaises(HTTPNotFound) as cm:
            Client.device.post_device_serialNo_models(
                serialNo="A0", modelInstances=mod_insts).result()

        self._assert_error_msg(cm.exception, "no model with id 'XYZ' exists")


class TestBadRequests(unittest.TestCase, utils.ErrorReqMixin):
    def test_model_schema_violation(self):
        """
        Test creating new model, where model argument violates json schema
        """
        with self.assertRaises(HTTPBadRequest) as cm:
            Client.models.post_models_new(
                     modelFile="dummy_data",
                     model=json.dumps(dict(name=3))).result()

        self._assert_error_msg_contains(cm.exception, "Failed validating")


class TestDelUsedModel(utils.ModelMakerMixin,
                       utils.ErrorReqMixin,
                       unittest.TestCase):
    """
    test deleting a model that is instantiated on a device
    """
    def create_instance(self):
        mod_insts = ModelInstances(modelInstances=[
            ModelInstance(name="inst0",
                          model=self.modelId),
        ])
        Client.device.post_device_serialNo_models(
            serialNo=utils.TEST_DEVICE, modelInstances=mod_insts).result()

    def delete_instance(self):
        Client.device.post_device_serialNo_models(
            serialNo=utils.TEST_DEVICE,
            modelInstances=ModelInstances(modelInstances=[])
        ).result()

    def setUp(self):
        self.create_model()
        self.create_instance()

    def tearDown(self):
        self.delete_instance()
        self.delete_model()

    def test_del_used(self):
        """
        check that we get an 'bad request' when trying to delete a model
        which is instantiated on a device
        """
        with self.assertRaises(HTTPBadRequest) as cm:
            self.delete_model().result()

        self._assert_error_msg_contains(cm.exception, "model instantiated on")

import unittest
import json
from utils import Client, ModelStatus, Position, ModelInstances, ModelInstance

# we assume that this device exists on the host
# e.g. this device must be present to run the
# tests in this file
TEST_DEVICE = "A0"

def get_new_model_json(name, description, position):
    md = {
        "name": name,
        "description": description,
        "defaultPosition": { "sweref99": position.sweref99 },
    }
    return json.dumps(md)


class ModelMakerMixin:
    MOD_NAME = "test model"
    MOD_DESK = "model description"
    DEF_POS = Position(
        sweref99 = {
            "projection": "18 00",
            "x": 6175471.9873,
            "y": 300000.1234,
            "z": 68.0223,
            "yaw": 0.0,
            "roll" : 0.0,
            "pitch" : 0.0,
    })

    def create_model(self):
        model_str = get_new_model_json(self.MOD_NAME, self.MOD_DESK, self.DEF_POS)
        res = Client.models.post_models_new(modelFile="dummy_data",
                                            model=model_str).result()
        self.modelId = res["model"]

    def delete_model(self):
        #
        # Delete created model
        #
        res = Client.models.delete_models_modelId(modelId=self.modelId).result()
        self.assertIsNone(res)


class TestModel(unittest.TestCase, ModelMakerMixin):
    """
    Test creating, updating, getting and deleting model.
    """
    def setUp(self):
        self.create_model()

    def tearDown(self):
        self.delete_model()

    def test_get(self):
        """
        Tests creating a model, getting and deleting that model.
        (the creation and deletion are tested implicitly)
        """
        mod_status = Client.models.get_models_modelId(modelId=self.modelId).result()
        self.assertEqual(mod_status,
                         ModelStatus(name=self.MOD_NAME,
                                     description=self.MOD_DESK,
                                     defaultPosition=self.DEF_POS,
                                     importStatus="processing"))

    def test_update(self):
        """
        Test updating a model
        """
        NEW_NAME = "new name"
        NEW_DESC = "new desc"

        # update model
        Client.models.put_models_modelId(
            modelId=self.modelId,
            modelUpdate=dict(name=NEW_NAME,
                             description=NEW_DESC)).result()

        # get model and check that it got new name and description
        mod_status = Client.models.get_models_modelId(modelId=self.modelId).result()
        self.assertEqual(mod_status,
                         ModelStatus(name=NEW_NAME,
                                     description=NEW_DESC,
                                     defaultPosition=self.DEF_POS,
                                     importStatus="processing"))


class TestInstances(unittest.TestCase, ModelMakerMixin):
    """
    Test model instances API requests
    """
    def create_instances(self):
        mod_insts = ModelInstances(modelInstances=[
            ModelInstance(name="inst0",
                          model=self.modelId),
            ModelInstance(name="inst1",
                          model=self.modelId),
        ])
        Client.device.post_device_serialNo_models(
            serialNo=TEST_DEVICE, modelInstances=mod_insts).result()

    def delete_instances(self):
        Client.device.post_device_serialNo_models(
            serialNo=TEST_DEVICE, modelInstances=ModelInstances(modelInstances=[])).result()

    def setUp(self):
        self.create_model()
        self.create_instances()

    def tearDown(self):
        self.delete_model()
        self.delete_instances()

    def test_get(self):
        """
        test getting current model instances
        """
        res = Client.device.get_device_serialNo_models(serialNo=TEST_DEVICE).result()
        instances = [
            ModelInstance(
                name="inst%s" % n,
                hidden=False,
                model=self.modelId,
                position=self.DEF_POS,
            ) for n in range(2)]
        self.assertEqual(res, ModelInstances(modelInstances=instances))

    def test_update(self):
        """
        test updating a device's current model instances
        """

        # set new model instances
        mod_insts = ModelInstances(modelInstances=[
            ModelInstance(name="new_inst",
                          model=self.modelId)])
        Client.device.post_device_serialNo_models(
            serialNo=TEST_DEVICE, modelInstances=mod_insts).result()

        # get model instances, and check that they have been updated
        res = Client.device.get_device_serialNo_models(serialNo=TEST_DEVICE).result()
        self.assertEqual(res, ModelInstances(modelInstances=[ModelInstance(
                name="new_inst",
                hidden=False,
                model=self.modelId,
                position=self.DEF_POS,
            )]))

    def test_delete(self):
        """
        Test deleting model instances
        """
        self.delete_instances()

        # check that model instances list is empty
        res = Client.device.get_device_serialNo_models(serialNo=TEST_DEVICE).result()
        self.assertEqual(res, ModelInstances(modelInstances=[]))


class TestDevices(unittest.TestCase):
    def test_get(self):
        res = Client.devices.get_devices().result()

        # do a simple validation of the results,
        # where we assume that XXX000001 and XXX000002
        # devices are in the database
        #
        # TODO: make a proper validation by crosschecking with database
        # TODO: or by adding some known devices to the database
        serNums = [d.serialNo for d in res.devices]
        self.assertIn("XXX000001", serNums)
        self.assertIn("XXX000002", serNums)

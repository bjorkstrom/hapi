import unittest
from .. import settings
from .import utils
from .utils import Client, ModelStatus, ModelInstances, ModelInstance


class TestModel(unittest.TestCase, utils.ModelMakerMixin):
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
        mod_status = Client.models.get_models_modelId(
            modelId=self.modelId
        ).result()
        self.assertEqual(mod_status,
                         ModelStatus(name=self.MOD_NAME,
                                     description=self.MOD_DESK,
                                     defaultPosition=self.DEF_POS,
                                     importStatus="processing"))

    def test_get_all(self):
        """
        test getting all models
        """
        res = Client.models.get_models().result()

        # validate result by checking that created model's ID is
        # included into the results
        mod_ids = [m.model for m in res.models]
        self.assertIn(self.modelId, mod_ids)

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
        mod_status = Client.models.get_models_modelId(
            modelId=self.modelId
        ).result()
        self.assertEqual(mod_status,
                         ModelStatus(name=NEW_NAME,
                                     description=NEW_DESC,
                                     defaultPosition=self.DEF_POS,
                                     importStatus="processing"))


class TestInstances(unittest.TestCase, utils.ModelMakerMixin):
    """
    Test model instances API requests
    """
    INST_NAME = "test instance"
    INST_DESK = "instance description"
    INST_POS = utils.Position(
        sweref99={
            "projection": "13 30",
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
            "yaw": 4.0,
            "roll": 5.0,
            "pitch": 6.0,
        }
    )

    def create_instances(self):
        mod_insts = ModelInstances(modelInstances=[

            # first instance should inherit it's name,
            # description and position from the model
            ModelInstance(model=self.modelId),

            # second instance overrides model's name,
            # description and position
            ModelInstance(name=self.INST_NAME,
                          description=self.INST_DESK,
                          position=self.INST_POS,
                          model=self.modelId),
        ])
        Client.device.post_device_serialNo_models(
            serialNo=settings.TEST_DEVICE, modelInstances=mod_insts).result()

    def delete_instances(self):
        Client.device.post_device_serialNo_models(
            serialNo=settings.TEST_DEVICE,
            modelInstances=ModelInstances(modelInstances=[])
        ).result()

    def setUp(self):
        self.create_model()
        self.create_instances()

    def tearDown(self):
        self.delete_instances()
        self.delete_model()

    def test_get(self):
        """
        test getting current model instances
        """
        res = Client.device.get_device_serialNo_models(
            serialNo=settings.TEST_DEVICE
        ).result()

        instances = [
            # first instance should have values from the model
            ModelInstance(
                name=self.MOD_NAME,
                description=self.MOD_DESK,
                position=self.DEF_POS,
                hidden=False,
                model=self.modelId,
            ),
            # second instance should override values
            ModelInstance(
                name=self.INST_NAME,
                description=self.INST_DESK,
                hidden=False,
                model=self.modelId,
                position=self.INST_POS,
            ),
        ]
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
            serialNo=settings.TEST_DEVICE, modelInstances=mod_insts).result()

        # get model instances, and check that they have been updated
        res = Client.device.get_device_serialNo_models(
            serialNo=settings.TEST_DEVICE
        ).result()
        self.assertEqual(res, ModelInstances(modelInstances=[ModelInstance(
                name="new_inst",
                description=self.MOD_DESK,
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
        res = Client.device.get_device_serialNo_models(
            serialNo=settings.TEST_DEVICE
        ).result()
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

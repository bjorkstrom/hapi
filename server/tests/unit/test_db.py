import unittest
from unittest import mock
from .. import settings
from hapi import database
from hapi.rest import device
from hapi.dbmodels import Model, SwerefPos, Device, ModelInstance


def _pos():
    return {
            "sweref99": {
                "projection": "18 00",
                "x": 6175471.9873,
                "y": 300000.1234,
                "z": 68.0223,
            }
        }


def _new_model_dict(default_pos=True):
    mod_dict = {
        "name": "test-model",
        "description": "my test model",
        "placement": "global",
    }

    if default_pos:
        mod_dict["defaultPosition"] = _pos()

    return mod_dict


def create_new_model(default_pos=True):
    mod = Model.from_dict(_new_model_dict(default_pos))

    database.db_session.add(mod)
    database.db_session.commit()

    return mod


def flask_req_mock():
    """
    Create a moock or flask.request object,
    with authorization set to test user's credentials
    :return:
    """
    req = mock.Mock()
    req.authorization.username = settings.TEST_USER
    req.authorization.password = settings.TEST_PASSWD

    return req


def instantiate_model(modelId, position=True):
    d = {
        "modelInstances": [
            {
                "description": "string",
                "hidden": True,
                "model": modelId,
                "name": "string",
            }
        ]
    }

    if position:
        d["modelInstances"][0]["position"] = _pos()

    resp = device.post(settings.TEST_DEVICE, d)
    assert resp.status_code == 204


def del_model_instances():
    resp = device.post(settings.TEST_DEVICE, {"modelInstances": []})
    assert resp.status_code == 204


class TestModel(unittest.TestCase):
    def test_del_with_default_pos(self):
        """
        create and delete a model with default position specified

        check that both model and default position are removed
        from the database
        """

        # create model
        model = create_new_model()

        # save default position ID for later checks
        model_id = model.id
        def_pos_id = Model.get(model.id).default_position.id

        # delete model
        session = database.db_session
        model.delete(session)
        session.commit()

        # check that both model and default position rows
        # have been deleted from the database
        assert Model.get(model_id) is None
        assert SwerefPos.query.filter(SwerefPos == def_pos_id).first() is None

    def test_del_without_default_pos(self):
        """
        create and delete a model without default position
        """
        # create model
        model = create_new_model(default_pos=False)
        model_id = model.id

        # check that no default position was stored in the database
        assert model.default_position is None

        # delete model
        session = database.db_session
        model.delete(session)
        session.commit()

        # check that the model have been deleted from the database
        assert Model.get(model_id) is None


@mock.patch("flask.request", flask_req_mock())
class TestModelInstance(unittest.TestCase):
    def setUp(self):
        self.model = create_new_model()

    def tearDown(self):
        session = database.db_session
        self.model.delete(session)
        session.commit()

    def test_del_instance_with_position(self):
        """
        create and delete a model instances with a position

        check in the database that both model instance and position
        rows have been deleted
        """
        # create model instance
        instantiate_model(self.model.id)

        dev = Device.get(settings.TEST_DEVICE)
        # there should be one model instance
        assert len(dev.model_instances) == 1

        # save instance and position ID for later checks
        mod_inst = dev.model_instances[0]
        inst_id = mod_inst.id
        pos_id = mod_inst.position.id

        # delete model instance
        del_model_instances()

        # check that both model instance and it's position
        # have been deleted from the database
        mi = ModelInstance.query.filter(ModelInstance.id == inst_id).first()
        assert mi is None
        assert SwerefPos.query.filter(SwerefPos.id == pos_id).first() is None

    def test_del_instance_no_position(self):
        """
        create and delete a model instances without a position specified
        """

        # create model instance
        instantiate_model(self.model.id, position=False)

        dev = Device.get(settings.TEST_DEVICE)
        # there should be one model instance
        assert len(dev.model_instances) == 1

        # save instance and position ID for later checks
        mod_inst = dev.model_instances[0]
        inst_id = mod_inst.id

        # delete model instance
        del_model_instances()

        # check that both model instance
        # have been deleted from the database
        mi = ModelInstance.query.filter(ModelInstance.id == inst_id).first()
        assert mi is None

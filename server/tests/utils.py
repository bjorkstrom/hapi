import json
from bravado.client import SwaggerClient

Client = SwaggerClient.from_url("http://localhost:9090/v1/swagger.json")


ModelInstances = Client.get_model("ModelInstances")
ModelInstance = Client.get_model("ModelInstance")
ModelStatus = Client.get_model("ModelStatus")
Position = Client.get_model("Position")
EventSubscription = Client.get_model("EventSubscription")
EventFilter = Client.get_model("EventFilter")
RestEndpoint = Client.get_model("RestEndpoint")


class ErrorReqMixin:
    def _assert_error_msg(self, exception, err_msg):
        self.assertEqual(exception.swagger_result.message, err_msg)

    def _assert_error_msg_contains(self, exception, err_msg_part):
        self.assertIn(err_msg_part, exception.swagger_result.message)


def get_new_model_json(name, description, position):
    md = {
        "name": name,
        "description": description,
        "placement": "global",
        "defaultPosition": {"sweref99": position.sweref99},
    }
    return json.dumps(md)


class ModelMakerMixin:
    MOD_NAME = "test model"
    MOD_DESK = "model description"
    DEF_POS = Position(
        sweref99={
            "projection": "18 00",
            "x": 6175471.9873,
            "y": 300000.1234,
            "z": 68.0223,
            "yaw": 0.0,
            "roll": 0.0,
            "pitch": 0.0,
        }
    )

    def create_model(self):
        model_str = get_new_model_json(
            self.MOD_NAME, self.MOD_DESK, self.DEF_POS)
        res = Client.models.post_models_new(modelFile="dummy_data",
                                            model=model_str).result()
        self.modelId = res["model"]

    def delete_model(self):
        #
        # Delete created model
        #
        res = Client.models.delete_models_modelId(
            modelId=self.modelId
        ).result()
        self.assertIsNone(res)

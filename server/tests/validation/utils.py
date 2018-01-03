import json
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from .. import settings


def _get_client():
    host = "localhost"

    http_client = RequestsClient()
    http_client.set_basic_auth(host,
                               settings.TEST_USER,
                               settings.TEST_PASSWD)
    swagger_url = "http://%s:9090/v1/swagger.json" % host

    return SwaggerClient.from_url(swagger_url,
                                  http_client=http_client)


Client = _get_client()


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


class SubscriptionMakerMixin:
    def make_subscription(self,
                          dest_url="http://example.com/foo",
                          headers=[],
                          topics=["topic1", "topic2"],
                          duration=10):
        endpoint = RestEndpoint(
            URL=dest_url,
            method="POST",
            headers=headers,
        )

        event_filters = [EventFilter(topic=t) for t in topics]

        subscription = EventSubscription(
            duration=duration,
            eventFilters=event_filters,
            destination={'restEndpoint': endpoint},
        )
        res = Client.device.post_device_serialNo_events_subscriptions_new(
            serialNo="A0",
            Subscription=subscription,

        ).result()

        self.subscriptionID = res.subscriptionID

    def cancel_subscription(self):
        dev = Client.device
        dev.delete_device_serialNo_events_subscriptions_subscriptionID(
            serialNo="A0",
            subscriptionID=self.subscriptionID,
        ).result()

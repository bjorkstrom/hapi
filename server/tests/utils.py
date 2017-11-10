from bravado.client import SwaggerClient

Client = SwaggerClient.from_url("http://localhost:9090/v1/swagger.json")

ModelInstances = Client.get_model("ModelInstances")
ModelInstance = Client.get_model("ModelInstance")


class ErrorReqMixin:
    def _assert_error_msg(self, exception, err_msg):
        self.assertEqual(exception.swagger_result.message, err_msg)

    def _assert_error_msg_contains(self, exception, err_msg_part):
        self.assertIn(err_msg_part, exception.swagger_result.message, )



from connexion import resolver

#
# A simple operations ID resolver.
#
# We just statically map (method, path) tuple to an operation ID.
#
# The operational ID is then mapped to a function to call by connexion
# machinery.
#
# The mapping is a simple lookup of the functions full name, e.g.
#
# for operation id 'foo.bar.moin' the function moin()
# in foo.bar module is called.
#

#
# note: All operation ID in this table are prefixed with 'hapi.rest'
#
OPS_MAP = {
    ("get", "/device/{serialNo}/models"):
        "device.get",
    ("post", "/models/new", ):
        "models.post",
    ("put", "/models/{modelId}"):
        "models.put",
    ("get", "/models"):
        "models.search",
    ("get", "/devices"):
        "devices.search",
    ("get", "/models/{modelId}"):
        "models.get",
    ("post", "/device/{serialNo}/models"):
        "device.post",
    ("delete", "/models/{modelId}"):
        "models.delete",
    ("post", "/device/{serialNo}/events-subscriptions/new"):
        "subscription.new",
    ("post", "/device/{serialNo}/events-subscriptions/{subscriptionID}"):
        "subscription.renew",
    ("delete", "/device/{serialNo}/events-subscriptions/{subscriptionID}"):
        "subscription.cancel",
}


class HagringResolver(resolver.Resolver):
    def resolve_operation_id(self, operation):
        return "hapi.rest." + OPS_MAP[(operation.method, operation.path)]

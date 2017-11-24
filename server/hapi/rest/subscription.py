import flask


def new(serialNo, Subscription):
    print("serialNo %s" % serialNo)
    import pprint
    pprint.pprint(Subscription)
    return dict(subscriptionID="XXX")


def renew(serialNo, subscriptionID, subscription):
    print(serialNo, subscriptionID, subscription)
    return flask.Response(status=204)


def cancel(serialNo, subscriptionID):
    print("cancel ", serialNo, subscriptionID)
    return flask.Response(status=204)

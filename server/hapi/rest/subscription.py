import flask
from . import util
from hapi.dbmodels import Device
from hapi import database
from hapi import dbmodels


def _invalid_subScription_resp(Subscription):
    msg = "No subscription"
    return dict(message=msg), 404


# Create new subscription event
def new(serialNo, Subscription):
    device = Device.get(serialNo)
    if device is None:
        return util.device_not_found_resp(serialNo)

    session = database.db_session
    sub = dbmodels.Subscription.from_dict(device, Subscription)
    session.add(sub)
    session.commit()
    return dict(subscriptionID=str(sub.id))


# Renew subscription
def renew(serialNo, subscriptionID, subscription):
    session = database.db_session
    sub = dbmodels.Subscription.get(subscriptionID)
    if sub is None:
        return _invalid_subScription_resp(subscriptionID)
    sub.expiration = dbmodels.Subscription.get_Expiration(
        subscription["duration"])
    session.add(sub)
    session.commit()
    return flask.Response(status=204)


# Delete subscription
def cancel(serialNo, subscriptionID):
    sub = dbmodels.Subscription.get(subscriptionID)
    if sub is None:
        return _invalid_subScription_resp(subscriptionID)
    session = database.db_session
    sub.delete(session)
    session.commit()

    return flask.Response(status=204)

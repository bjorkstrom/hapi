import flask
from hapi.dbmodels import Device, RestEndpoint
from hapi import database
from hapi import dbmodels

from . import util

def _device_not_found_resp(serialNo):
    msg = "no device with serial number '%s' exists" % serialNo
    return dict(message=msg), 404


def _invalid_subScription_resp(Subscription):
    msg = "No subscription"
    return dict(message=msg), 404


def new(serialNo, Subscription):
    print("New Subscription serialNo %s" % serialNo)
    device = Device.get(serialNo)
    if device is None:
        return _device_not_found_resp(serialNo)
     
    session = database.db_session   
    try:
        sub = dbmodels.Subscription.from_dict(device, Subscription)
        session.add(sub)
    except SubscriptionNotFound as e:
        return _invalid_subScription_resp(e)
    
    session.commit()
    return dict(subscriptionID=str(sub.id))
  

def renew(serialNo, subscriptionID, subscription):    
    print(serialNo, subscriptionID, subscription)
    return flask.Response(status=204)


def cancel(serialNo, subscriptionID):
    sub = dbmodels.Subscription.get(subscriptionID)
    if sub is None:
        return _invalid_subScription_resp(sub)
    restEndpoint = sub.restEndpoint
    database.db_session.delete(restEndpoint)
    database.db_session.commit()

    print("cancel subscription ", serialNo, subscriptionID)
    return flask.Response(status=204)

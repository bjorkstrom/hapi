from hapi.dbmodels import Device


#
# GET /devices
#
def search():
    # not sure why connexion maps the request to 'search' function
    return dict(devices=[d.as_dict() for d in Device.all()])

from decorator import decorator
from hapi.dbmodels import User, Device
import bcrypt
import flask


def authenticate():
    '''Sends a 401 response that enables basic auth'''
    return flask.Response('You have to login with proper credentials', 401,
                          {'WWW-Authenticate': 'Basic realm="Login Required"'})


def _check_password(obj, password):
    if obj is None:
        return False

    return bcrypt.checkpw(password.encode("utf-8"),
                          obj.password.encode("utf-8"))


def check_user(username, password):
    return _check_password(User.get(username), password)


def check_device(serialNo, password):
    return _check_password(Device.get(serialNo), password)


@decorator
def user(f: callable, *args, **kwargs):
    auth = flask.request.authorization
    if not auth or not check_user(auth.username, auth.password):
        return authenticate()
    return f(*args, **kwargs)


@decorator
def device(f: callable, *args, **kwargs):
    auth = flask.request.authorization
    if not auth or not check_device(auth.username, auth.password):
        return authenticate()
    return f(*args, **kwargs)

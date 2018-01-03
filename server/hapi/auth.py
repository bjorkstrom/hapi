from hapi.dbmodels import User, Device
import bcrypt
import flask


def _authenticate():
    """Sends a 401 response that enables basic auth"""
    return flask.Response("You have to login with proper credentials", 401,
                          {'WWW-Authenticate': 'Basic realm="Login Required"'})


def _check_password(obj, password):
    if obj is None:
        return False

    return bcrypt.checkpw(password.encode("utf-8"),
                          obj.password.encode("utf-8"))


def _creds_ok(checks):
    auth = flask.request.authorization
    if not auth:
        return False

    for c in checks:
        if c(auth.username, auth.password):
            return True

    return False


def user(username, password):
    return _check_password(User.get(username), password)


def device(serialNo, password):
    return _check_password(Device.get(serialNo), password)


def allow(*checks):
    def _wrapper(f: callable):
        def _do_checks(*args, **kwargs):
            if not _creds_ok(checks):
                return _authenticate()
            return f(*args, **kwargs)
        return _do_checks

    return _wrapper

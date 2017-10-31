import bson

def update(modelID, body):
    print("update model %s to %s" % (modelID, body))
#    body = bson.loads(user)
#    print(body, type(body))

def get(modelID):
    print("get model %s" % (modelID))


def delete(modelID):
    print("DEL model %s" % (modelID))


def new(user):
    body = bson.loads(user)
    print(body, type(body))

def model_not_found_resp(modelId):
    msg = "no model with id '%s' exists" % modelId
    return dict(message=msg), 404

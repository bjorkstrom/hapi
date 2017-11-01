#
# Handles uploads of new models
#

import bson
import jsonschema
import database
from dbmodels import Model
from jsonschema.exceptions import ValidationError


class InvalidModel(Exception):
    pass


#
# We specify the schema for new model structure here,
# because it seems it't not possible to specify schema for
# bson POST request in swagger 2.0
#
MODEL_SCHEMA = {
    "type": "object",
    "properties":
    {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "data": {
            "type": "object",
            "properties": {
                "filename": {"type" : "string"},
                # can't specify schema for 'content',
                # as it's should be of 'bytes' type,
                # don't think that's supported by json schema
            },
        },
    },
    "required": ["data"],
}


def _parse_model_bson(bson_bytes):
    try:
        mod_dict = bson.loads(bson_bytes)
    except Exception:
        raise InvalidModel("malformed bson data")

    return mod_dict


def _validate_content_field(data):
    """
    manually validate model["data"]["content"] field,
    as we can't express required type with json schema
    """
    if "content" not in data:
        raise InvalidModel("missing model.data.content field")

    if not isinstance(data["content"], bytes):
        raise InvalidModel("model.data.content field is not binary data")


def _validate_model_dic(model_dict):
    try:
        jsonschema.validate(model_dict, MODEL_SCHEMA)
        _validate_content_field(model_dict["data"])
    except ValidationError as e:
        raise InvalidModel("invalid model description: %s" % str(e))


def add_model(model_bson):
    mod_dict = _parse_model_bson(model_bson)
    _validate_model_dic(mod_dict)
    mod = Model.from_dict(mod_dict)

    database.db_session.add(mod)
    database.db_session.commit()

    return mod.id

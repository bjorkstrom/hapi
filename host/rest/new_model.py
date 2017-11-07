#
# Handles uploads of new models
#

import os
from os import path
import json
import jsonschema
import database
from dbmodels import Model
from jsonschema.exceptions import ValidationError


MODEL_FILE_DIR = "model_files"


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
        "defaultPosition": {
            "type": "object",
            "properties": {
                "sweref99": {
                    "type": "object",
                    "properties": {
                        "projection": {
                            "type": "string",
                            "enum": [
                                "TM", "12 00", "13 30", "15 00", "16 30",
                                "18 00", "14 15", "15 45", "17 15", "18 45",
                                "20 15", "21 45", "23 15",
                            ],
                        },
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "z": {"type": "number"},
                        "roll": {"type": "number"},
                        "pitch": {"type": "number"},
                        "yaw": {"type": "number"},
                    },
                    "required": ["projection", "x", "y", "z"],
                },
            },
        },
    },
}


def _parse_model_json(json_str):
    try:
        mod_dict = json.loads(json_str)
    except Exception:
        raise InvalidModel("malformed json data")

    return mod_dict


def _validate_model_dic(model_dict):
    try:
        jsonschema.validate(model_dict, MODEL_SCHEMA)
    except ValidationError as e:
        raise InvalidModel("invalid model description: %s" % str(e))


def _save_file(modelFile, modelId):
    os.makedirs(MODEL_FILE_DIR, exist_ok=True)

    fpath = path.join(MODEL_FILE_DIR, "mod%s" % modelId)
    with open(fpath, "wb") as f:
        f.write(modelFile.read())


def add_model(modelFile, model):
    mod_dict = _parse_model_json(model)
    _validate_model_dic(mod_dict)

    mod = Model.from_dict(mod_dict)

    database.db_session.add(mod)
    database.db_session.commit()

    _save_file(modelFile, mod.id)

    return mod.id

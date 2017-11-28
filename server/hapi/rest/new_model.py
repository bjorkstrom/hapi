#
# Handles uploads of new models
#

import json
import yaml
import os
from os import path

import jsonschema
from hapi.dbmodels import Model
from hapi import database
from jsonschema.exceptions import ValidationError

MODEL_FILE_DIR = "model_files"


class InvalidModel(Exception):
    pass

#
# We use an external json schema file to validate
# the new model json metadata.
#
# This is due to the fact that in swagger 2.0 it's not
# possible to specify json format for one of the parts
# in a multipart/form-data POST request.
#


ModelSchema = None


def _get_model_schema():
    """
    lazy-load and parse the ../swagger/model.yaml file
    """
    global ModelSchema

    def _load_model_schema():
        # figure out the ../swagger/model.yaml path
        # using this source file's path
        root_dir, _ = path.split(path.dirname(__file__))
        sch_path = path.join(root_dir, "swagger", "model.yaml")

        with open(sch_path, "r") as f:
            return yaml.load(f)

    if ModelSchema is None:
        ModelSchema = _load_model_schema()

    return ModelSchema


def _parse_model_json(json_str):
    try:
        mod_dict = json.loads(json_str)
    except Exception:
        raise InvalidModel("malformed json data")

    return mod_dict


def _validate_model_dic(model_dict):
    try:
        jsonschema.validate(model_dict, _get_model_schema())
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

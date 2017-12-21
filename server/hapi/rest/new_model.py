#
# Handles uploads of new models
#

import json
import yaml
from os import path
import boto3
import jsonschema
from hapi.dbmodels import Model
from hapi import database
from jsonschema.exceptions import ValidationError
from hapi import config

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


def _s3_key(model_id, user_id, mod_file_ext):
    return "assets/%s/%s/source.%s" % (user_id, model_id, mod_file_ext)


def _sqs_msg(model_id, user_id, mod_file_ext):
    msg = dict(
        owner=user_id,
        model=model_id,
        type=mod_file_ext,
        env=config.BRAB_ENV,
        importer_version=config.IMPORTER_VERSION)

    return json.dumps(msg)


def _publish_file(model_file, model_id, user_id):

    _, ext = path.splitext(model_file.filename)
    if ext.startswith("."):
        ext = ext[1:]

    s3_client = boto3.client("s3")
    s3_client.upload_fileobj(model_file,
                             config.AWS_ASSET_BUCKET,
                             _s3_key(model_id, user_id, ext))

    sqs_client = boto3.client(
        "sqs",
        region_name=config.AWS_REGION)

    sqs_client.send_message(
        QueueUrl=config.AWS_SQS_URL,
        MessageBody=_sqs_msg(model_id, user_id, ext)
    )


def add_model(model_file, model, user):
    mod_dict = _parse_model_json(model)
    _validate_model_dic(mod_dict)

    mod = Model.from_dict(mod_dict)
    mod.uploader = user
    mod.organization = user.organization

    database.db_session.add(mod)
    database.db_session.commit()

    _publish_file(model_file, mod.id, user.id)

    return mod.id

import boto3
from hapi import config


def delete_models_s3_objs(model_id, user_id):
    s3_client = boto3.client("s3")

    #
    # S3 API only supports deleting an explicit list of
    # objects, it's not possible to delete 'folders'
    # so in order to delete all objects belonging to
    # a model, we first need to list the contests of
    # the model's folder
    #

    # generate a list of all the model's objects
    key_prefix = "assets/%s/%s" % (user_id, model_id)
    resp = s3_client.list_objects(
        Bucket=config.AWS_ASSET_BUCKET,
        Prefix=key_prefix)
    objs = [dict(Key=c["Key"]) for c in resp["Contents"]]

    # delete all objects found
    s3_client.delete_objects(
        Bucket="apitest-models",
        Delete={"Objects": objs})

import hashlib
import logging

import boto3
from botocore.exceptions import ClientError

from config import (
    AWS_BUCKET_NAME,
    TARIC_FILES_FOLDER,
    TARIC_FILES_INDEX,
    STREAM_CHUNK_SIZE,
    S3_ENDPOINT_URL,
)

logger = logging.getLogger("taricapi.files3")

sid = None


# AWS S3 session
def session():
    # return cached client id
    global sid  # pylint: disable=W0603
    if sid is not None:
        return sid

    try:
        s3c = boto3.client("s3", endpoint_url=S3_ENDPOINT_URL)
        sid = s3c
    except ClientError:
        logger.error("Error connecting to AWS S3")
        return None

    return s3c


# -------------------------------------------------
# File Handling functions
# Note these are to provide a level of abstraction
# - e.g. database or S3 could be physical locations
# -------------------------------------------------


# generic file functions
def modification_date(filepath):
    response = session().get_object(Bucket=AWS_BUCKET_NAME, Key=filepath)
    md = response["Metadata"]
    if "modified" in md:
        modtime = md["modified"]
    else:
        modtime = response["LastModified"].isoformat()[:19]

    return modtime


def find(list_, key, value):
    for i, dic in enumerate(list_):
        if dic[key] == value:
            return i
    return -1


def file_exists(filename):
    try:
        session().get_object(Bucket=AWS_BUCKET_NAME, Key=filename)
        return True

    except session().exceptions.NoSuchKey:
        return False

    except ClientError as e:
        logger.error("Error occurred in get_object for %s: %s", filename, e)
        return None


def get_file(filepath):
    try:
        response = session().get_object(Bucket=AWS_BUCKET_NAME, Key=filepath)
        return response["Body"]

    except ClientError as e:
        logger.error("Error opening %s: %s", filepath, e)
        return None


def get_file_size(filepath):
    try:
        response = session().get_object(Bucket=AWS_BUCKET_NAME, Key=filepath)
        return response["ContentLength"]

    except ClientError as e:
        logger.error("Error opening %s: %s", filepath, e)
        return None


def read_file(filepath):
    generator = stream_file(filepath)
    return b"".join(x for x in generator)


def stream_file(filepath):
    try:
        obj = session().get_object(Bucket=AWS_BUCKET_NAME, Key=filepath)

    except session().exceptions.NoSuchKey as e:
        logger.error("Error opening %s: %s", filepath, e)
        raise e

    else:
        while True:
            chunk = obj["Body"].read(STREAM_CHUNK_SIZE)
            if chunk:
                yield chunk
            else:
                break


def write_file(filepath, jsoncontent):
    session().put_object(Body=jsoncontent, Bucket=AWS_BUCKET_NAME, Key=filepath)


def create_multipart_upload(filename):
    resp = session().create_multipart_upload(Bucket=AWS_BUCKET_NAME, Key=filename)
    logger.debug("%s", resp)
    return resp["UploadId"]


def upload_part(filename, uploadid, partnumber, bodypart):
    session().upload_part(
        Bucket=AWS_BUCKET_NAME,
        Key=filename,
        UploadId=uploadid,
        PartNumber=partnumber,
        Body=bodypart,
    )


def complete_multipart_upload(filename, uploadid):
    session().complete_multipart_upload(
        Bucket=AWS_BUCKET_NAME, Key=filename, UploadId=uploadid
    )


def abort_multipart_upload(filename, uploadid):
    session().abort_multipart_upload(
        Bucket=AWS_BUCKET_NAME, Key=filename, UploadId=uploadid
    )


def get_file_list(prefix):
    if prefix is None:
        prefix = TARIC_FILES_FOLDER
    files = session().list_objects(Bucket=AWS_BUCKET_NAME, Prefix=prefix)
    try:
        return files["Contents"]
    except KeyError:
        return []


def md5(filepath):
    hash_md5 = hashlib.md5()

    for chunk in stream_file(filepath):
        hash_md5.update(chunk)

    return hash_md5.hexdigest()


# Taric file specific functions
def get_taric_filepath(seq):
    return TARIC_FILES_FOLDER + "/" + seq + ".xml"


def get_temp_taric_filepath(seq):
    return TARIC_FILES_FOLDER + "/TEMP_" + seq + ".xml"


def get_taric_index_file():
    return TARIC_FILES_INDEX


def stream_taric_file(seq):
    if not file_exists(get_taric_filepath(seq)):
        return None

    return stream_file(get_taric_filepath(seq))


def save_temp_taric_file(file, seq):
    filename = get_temp_taric_filepath(seq)
    write_file(filename, file)
    return filename


def remove_temp_taric_file(seq):
    filename = get_temp_taric_filepath(seq)
    logger.debug("Removing file %s", filename)
    session().delete_object(Bucket=AWS_BUCKET_NAME, Key=filename)


def remove_taric_file(seq):
    """In ordinary operation taric files are not removed, but occasionally
    this is required.
    """
    filename = get_taric_filepath(seq)
    logger.debug("Removing file %s", filename)
    session().delete_object(Bucket=AWS_BUCKET_NAME, Key=filename)


def rename_file(fromname, toname):
    # AWS S3 has no rename - have to copy & delete
    logger.debug("Renaming file from %s to %s", fromname, toname)

    session().copy_object(
        Bucket=AWS_BUCKET_NAME,
        CopySource={"Bucket": AWS_BUCKET_NAME, "Key": fromname},
        Key=toname,
        MetadataDirective="COPY",
    )

    session().delete_object(Bucket=AWS_BUCKET_NAME, Key=fromname)


def rename_taric_file(seq, filetime):
    # AWS S3 has no rename - have to copy & delete
    logger.debug("Renaming temp file to %s", get_taric_filepath(seq))

    if filetime is not None:
        logger.debug("Setting Metadata modified to %s", filetime)
        session().copy_object(
            Bucket=AWS_BUCKET_NAME,
            CopySource={"Bucket": AWS_BUCKET_NAME, "Key": get_temp_taric_filepath(seq)},
            Key=get_taric_filepath(seq),
            Metadata={"modified": filetime},
            MetadataDirective="REPLACE",
        )
    else:
        session().copy_object(
            Bucket=AWS_BUCKET_NAME,
            CopySource={"Bucket": AWS_BUCKET_NAME, "Key": get_temp_taric_filepath(seq)},
            Key=get_taric_filepath(seq),
            MetadataDirective="REPLACE",
        )

    session().delete_object(Bucket=AWS_BUCKET_NAME, Key=get_temp_taric_filepath(seq))

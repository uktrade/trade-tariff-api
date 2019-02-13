import os
import boto3
import hashlib
import logging

from botocore.exceptions import ClientError

# Taric file location and Index name

TARIC_FILES_FOLDER = os.environ.get("TARIC_FILES_FOLDER", "taricfiles")
TARIC_FILES_INDEX = os.environ.get("TARIC_FILES_INDEX", "taricdeltas.json")

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME", "")

logger = logging.getLogger('taricapi-files3')

sid = None

def file_client(plogger):
    global logger
    logger = plogger

# AWS S3 session
def session():

    # return cached client id
    global sid
    if sid is not None:
        return sid

    if AWS_ACCESS_KEY_ID is not "" and AWS_SECRET_ACCESS_KEY is not "" and AWS_BUCKET_NAME is not "":

        try:
            s3c = boto3.client('s3',
                                aws_access_key_id = AWS_ACCESS_KEY_ID,
                                aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
            sid = s3c
        except ClientError:
            logger.error("Error connecting to AWS S3")
            return None

        return s3c
    else:
        return None


# -------------------------------------------------
# File Handling functions
# Note these are to provide a level of abstraction
# - e.g. database or S3 could be physical locations
# -------------------------------------------------

# generic file functions
def modification_date(filepath):
    response = session().get_object(Bucket = AWS_BUCKET_NAME,
                                    Key = filepath)
    print(response)
    md = response['Metadata']
    if 'modified' in md:
        modtime = md['modified']
    else:
        modtime = response['LastModified'].isoformat()[:19]

    return modtime

def find(list, key, value):
    for i, dic in enumerate(list):
        if dic[key] == value:
            return i
    return -1

def file_exists (prefix, file):
    try:
        allobjects = session().list_objects(Bucket = AWS_BUCKET_NAME,
                                            Prefix = prefix)
        if 'Contents' in allobjects:
            filelist = allobjects['Contents']
            filename = find(filelist, 'Key', file)

            return filename > -1
        else:
            return False

    except ClientError:
        logger.error ("Error retrieving list of objects in AWS")
        return False

def get_file(filepath):
    try:
        response = session().get_object(Bucket = AWS_BUCKET_NAME,
                                        Key = filepath)
        return response['Body']

    except ClientError:
        logger.error("Error opening " + filepath + " : ")
        return None

def get_file_size(filepath):
    try:
        response = session().get_object(Bucket = AWS_BUCKET_NAME,
                                        Key = filepath)
        return response['ContentLength']

    except ClientError:
        logger.error("Error opening " + filepath + " : ")
        return None

def read_file(filepath):
    try:
        response = session().get_object(Bucket = AWS_BUCKET_NAME,
                                        Key = filepath)
        return response['Body'].read()

    except ClientError:
        logger.error("Error opening " + filepath + " : ")
        return None

def write_file(filepath, jsoncontent):
 #   session().upload_fileobj(Fileobj = jsoncontent,
 #                            Bucket = AWS_BUCKET_NAME,
 #                            Key = filepath)

    session().put_object(Body = jsoncontent,
                         Bucket = AWS_BUCKET_NAME,
                         Key = filepath)

def create_multipart_upload(filename):
    resp = session().create_multipart_upload(Bucket = AWS_BUCKET_NAME,
                                             Key = filename)
    logger.debug(resp)
    return resp['UploadId']

def upload_part(filename, uploadid, partnumber, bodypart):
    session().upload_part(Bucket = AWS_BUCKET_NAME,
                          Key = filename,
                          UploadId = uploadid,
                          PartNumber = partnumber,
                          Body = bodypart)

def complete_multipart_upload(filename, uploadid):
    session().complete_multipart_upload(Bucket = AWS_BUCKET_NAME,
                                        Key = filename,
                                        UploadId = uploadid)

def abort_multipart_upload(filename, uploadid):
    session().abort_multipart_upload(Bucket = AWS_BUCKET_NAME,
                                        Key = filename,
                                        UploadId = uploadid)



def get_file_list(prefix):
    if prefix is None:
        prefix = TARIC_FILES_FOLDER
    files = session().list_objects(Bucket = AWS_BUCKET_NAME,
                                   Prefix = prefix)
    return files['Contents']


def md5(filepath):
    hash_md5 = hashlib.md5()
    hash_md5.update(read_file(filepath))
    return hash_md5.hexdigest()


# Taric file specific functions
def get_taric_filepath(seq):
    return TARIC_FILES_FOLDER + "/" + seq + ".xml"

def get_temp_taric_filepath(seq):
    return TARIC_FILES_FOLDER + "/TEMP_" + seq + ".xml"

def get_taric_index_file():
    return TARIC_FILES_INDEX

def read_taric_file(seq):
    return read_file(get_taric_filepath(seq))

def save_temp_taric_file(file, seq):
    filename = get_temp_taric_filepath(seq)
    write_file(filename, file)
    return filename

def remove_temp_taric_file(seq):
    filename = get_temp_taric_filepath(seq)
    logger.debug("Removing file " + filename)
    session().delete_object(Bucket = AWS_BUCKET_NAME,
                            Key = filename)

def rename_file(fromname, toname):
    # AWS S3 has no rename - have to copy & delete
    logger.debug("Renaming file from " + fromname + " to " + toname)

    session().copy_object (Bucket = AWS_BUCKET_NAME,
                           CopySource = {'Bucket': AWS_BUCKET_NAME, 'Key': fromname},
                           Key = toname,
                           MetadataDirective = 'COPY')

    session().delete_object(Bucket = AWS_BUCKET_NAME,
                            Key = fromname)

def rename_taric_file(seq, filetime):
    # AWS S3 has no rename - have to copy & delete
    logger.debug("Renaming temp file to " + get_taric_filepath(seq))
    logger.debug("Setting Metadata modified to " + filetime)

    session().copy_object (Bucket = AWS_BUCKET_NAME,
                           CopySource = {'Bucket': AWS_BUCKET_NAME, 'Key': get_temp_taric_filepath(seq)},
                           Key = get_taric_filepath(seq),
                           Metadata = {'modified': filetime},
                           MetadataDirective = 'REPLACE')

    session().delete_object(Bucket = AWS_BUCKET_NAME,
                            Key = get_temp_taric_filepath(seq))

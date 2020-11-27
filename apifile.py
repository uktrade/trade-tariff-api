import os
import time
import hashlib
import logging

from dateutil.tz import tzutc
from datetime import datetime


# Taric file location and Index name
from config import STREAM_CHUNK_SIZE

TARIC_FILES_FOLDER = os.environ.get("TARIC_FILES_FOLDER", "taricfiles")
TARIC_FILES_INDEX = os.environ.get("TARIC_FILES_INDEX", "taricdeltas.json")

logger = logging.getLogger('taricapi.file')


# -------------------------------------------------
# File Handling functions
# Note these are to provide a level of abstraction
# - e.g. database or S3 could be physical locations
# -------------------------------------------------

# generic file functions
def modification_date(filepath):
    t = os.path.getmtime(filepath)
    return datetime.fromtimestamp(t).isoformat()

def md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

def file_exists (prefix, file):
    return os.path.isfile(file)

def read_file(filepath):
    generator = stream_file(filepath)
    return ''.join(x for x in generator) if generator else None

def stream_file(filepath):
    try:
         f = open(filepath)
    except IOError as exc:
        logger.error("Error opening " + filepath + " : " + str(exc))
        yield None

    else:
        while True:
            chunk = f.read(STREAM_CHUNK_SIZE)
            if chunk:
                yield chunk
            else:
                break

def write_file(filepath, jsoncontent):
    with open(filepath, "w") as f:
        f.write(jsoncontent)

def get_file_list():
    files = [f for f in os.listdir(TARIC_FILES_FOLDER)
                if os.path.isfile(os.path.join(TARIC_FILES_FOLDER, f))]
    return files


# Taric file specific functions
def get_taric_filepath(seq):
    return os.path.join(TARIC_FILES_FOLDER + "/" + seq + ".xml")

def get_temp_taric_filepath(seq):
    return os.path.join(TARIC_FILES_FOLDER + "/TEMP_" + seq + ".xml")

def get_taric_index_file():
    return TARIC_FILES_INDEX

def stream_taric_file(seq):
    return stream_file(get_taric_filepath(seq))

def save_temp_taric_file(file, seq):
    filename = get_temp_taric_filepath(seq)
    file.save(filename)
    return filename

def remove_temp_taric_file(seq):
    filename = get_temp_taric_filepath(seq)
    logger.debug("Removing file " + filename)
    os.remove(filename)

def rename_taric_file(seq, filetime):
    logger.debug("Renaming temp file to " + get_taric_filepath(seq))
    os.rename(get_temp_taric_filepath(seq), get_taric_filepath(seq))

    if not filetime is None:
        filetime = dateutil.parser.parse(filetime)
        logger.info("Setting file time to " + str(filetime))
        filetimems = time.mktime(filetime.timetuple())
        os.utime(get_taric_filepath(seq), (filetimems, filetimems))

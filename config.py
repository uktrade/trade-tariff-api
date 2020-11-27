import json
import os


AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_BUCKET_NAME = os.environ['AWS_BUCKET_NAME']

API_ROOT = os.environ.get("API_ROOT", "http://localhost:8080/api/v1/")

APIKEYS = os.environ.get('APIKEYS','').split(',')
APIKEYS_UPLOAD = os.environ.get("APIKEYS_UPLOAD", "").split(',')
WHITELIST = os.environ.get("WHITELIST", "").split(',')
WHITELIST_UPLOAD = os.environ.get("WHITELIST_UPLOAD", "").split(',')

TARIC_FILES_FOLDER = os.environ.get("TARIC_FILES_FOLDER", "taricfiles")
TARIC_FILES_INDEX = os.environ.get("TARIC_FILES_INDEX", "taricdeltas.json")

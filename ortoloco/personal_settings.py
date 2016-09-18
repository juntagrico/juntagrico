import os

PHOTOLOGUE_GALLERY_SAMPLE_SIZE = 3

DEFAULT_FILE_STORAGE = 'ortoloco.utils.MediaS3BotoStorage'

try:
    AWS_ACCESS_KEY_ID = os.environ['ORTOLOCO_AWS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['ORTOLOCO_AWS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['ORTOLOCO_AWS_BUCKET_NAME']
except KeyError:
    raise KeyError('Need to define AWS environment variables: ' +
                   'AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_STORAGE_BUCKET_NAME')

# Default Django Storage API behavior - don't overwrite files with same name
AWS_S3_FILE_OVERWRITE = False

MEDIA_ROOT = 'media'

MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
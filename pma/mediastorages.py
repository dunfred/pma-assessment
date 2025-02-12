import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class StaticStorage(S3Boto3Storage):
    bucket_name     = settings.AWS_STORAGE_BUCKET_NAME
    region_name     = settings.AWS_S3_REGION_NAME
    location        = 'static'
    default_acl     = 'public-read'
    file_overwrite  = False

class MediaStorage(S3Boto3Storage):
    bucket_name     = settings.AWS_STORAGE_BUCKET_NAME
    region_name     = settings.AWS_S3_REGION_NAME
    location        = 'media'
    default_acl     = 'public-read'
    file_overwrite  = False

class PrivateMediaStorage(S3Boto3Storage):
    bucket_name     = settings.AWS_STORAGE_BUCKET_NAME
    region_name     = settings.AWS_S3_REGION_NAME
    location        = 'private'
    default_acl     = 'private'
    file_overwrite  = False
    custom_domain   = False
    querystring_auth = True
    querystring_expire = 1800  # Time in seconds (30 Minutes)

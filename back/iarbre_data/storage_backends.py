from storages.backends.s3boto3 import S3Boto3Storage


class PrivateMediaStorage(S3Boto3Storage):
    location = "private-media"
    default_acl = "private"
    file_overwrite = False
    custom_domain = False

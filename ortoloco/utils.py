from storages.backends.s3boto import S3BotoStorage

MediaS3BotoStorage = lambda: S3BotoStorage(location='media')
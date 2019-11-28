import boto3
import botocore
import gzip
import shutil
from io import BytesIO


class S3Manager:
    def __init__(self):
        try:
            self.s3 = boto3.client('s3')
        except Exception as e:
            print('Error while instantiating s3 manager: {}'.format(e.message))

    def download_file(self, bucket, key_object, local_filename, decompress=False):
        """
        Download object in a bucket
        :param bucket: bucket name, without s3://
        :param key_object: folder's and the file name
        :param local_filename: destine local filename
        :param decompress: True, file will be decompressed
        :return:
        """
        try:
            if decompress:
                data = self.s3.Object(bucket, key_object)
                n = data.get()['Body'].read()
                gzip_file = BytesIO(n)
                gzip_file = gzip.GzipFile(fileobj=gzip_file)
                with open(local_filename, 'wb') as outfile:
                    outfile.write(gzip_file.read())

            with open(local_filename, 'wb') as data:
                self.s3.download_fileobj(bucket, key_object, data)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                print("Some params are not correct")
                raise
            return False

        return True

    def upload_file(self, local_filename, bucket, key_object, compress=False):
        """
        Upload object in a bucket
        :param bucket: bucket name, without s3://
        :param key_object: folder's and the file name
        :param local_filename: source local complete
        :param compress: True, file will be compressed
        :return:
        """
        try:
            with open(local_filename, 'rb') as data:
                if compress:
                    compresed_io = BytesIO()
                    with gzip.GzipFile(fileobj=compresed_io, mode='wb') as out_gzp:
                        shutil.copyfileobj(data, out_gzp)
                    key_object = key_object + '.gz'
                    data = out_gzp
                self.s3.upload_fileobj(data, bucket, key_object)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                print("Some params are not correct")
                raise
            return False

        return True

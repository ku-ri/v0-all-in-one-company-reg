import boto3, botocore, os
from datetime import datetime


class S3Manager(object):
    def __init__(self):
        access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
        bucket_name = os.environ["AWS_S3_BUCKET_NAME"]
        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
        self.bucket = self.s3.Bucket(bucket_name)
        try:
            self.s3.meta.client.head_bucket(Bucket=self.bucket.name)
        except botocore.exceptions.ClientError as e:
            print("ERROR: Bucket not exist")
            raise (e)

    def download(self, key, file_path):
        try:
            self.bucket.download_file(key, file_path)
        except botocore.exceptions.ClientError as e:
            return None
        return file_path

    def get_resource_keys(self,corp_number_id):
        # get resource keys excluding directory type
        # return [obj.key for obj in self.bucket.objects.all() if not obj.key.endswith("/")]
        return corp_number_id + '.pdf'


    def get_last_modified_keys(self, last_modified_date):
        # get resource keys from the beginning of certain last modified date
        result = [obj.key for obj in self.bucket.objects.all() \
                  if datetime.strptime(str(obj.last_modified).split()[0], "%Y-%m-%d") \
                  >= datetime.strptime(last_modified_date, "%Y-%m-%d")]
        return result

    def get_pdf_object(self, file_path):
        obj = self.s3.Object(os.environ["AWS_S3_BUCKET_NAME"], file_path)
        pdf_open = obj.get()['Body'].read()

        return pdf_open

    def upload(self, key, file_path):
        # if os.path.isdir(file_path):
        #     return self.bulk_upload(file_path)
        self.bucket.upload_file( file_path,key)

    def bulk_upload(self, dir_path):
        files = os.listdir(dir_path)
        for f in files:
            self.upload("{}/{}".format(dir_path, f))

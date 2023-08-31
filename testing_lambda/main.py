from os import environ
from boto3 import client
from dotenv import load_dotenv
import datetime

def send_to_s3(s3_bucket):

    name = str(datetime.datetime.now()) + ".txt"
    s3_bucket.upload_file("placeholder.txt", "plants-vs-trainees-long-term-storage", name)

def handler(event=None, context=None):
    load_dotenv()
    s3_bucket = client("s3", aws_access_key_id=environ.get("ACCESS_KEY_ID"),
            aws_secret_access_key=environ.get("SECRET_ACCESS_KEY"))
    send_to_s3(s3_bucket)


if __name__ == "__main__":
    handler()

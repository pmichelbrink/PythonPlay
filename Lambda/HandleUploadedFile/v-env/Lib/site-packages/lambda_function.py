import boto3
import os
import uuid
from urllib.parse import unquote_plus
import imghdr
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            tmpkey = key.replace('/', '')
            download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
            s3_client.download_file(bucket, key, download_path)
            statinfo = os.stat(download_path)
            
            if (imghdr.what(download_path) == None):
                print('File is not an image. Deleting {}'.format(key))
            elif (statinfo.st_size > 10000000):
                print('File too large ({} bytes). Deleting {}'.format(statinfo.st_size, key))
            else:
                # Move the file to the non-public images bucket
                s3_client.upload_file(download_path, 'wtfthat-images', key)

                # Create a record in the DB
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table('Images')
                uid_str = uuid.uuid4().urn

                response = table.put_item(
                    Item = {
                        'Id': uid_str[9:],
                        'FileName': key,
                        'Created': datetime.now().isoformat(),
                        'LastServed': datetime(1970,1,1).isoformat(),
                        'ClassificationConfidence': 0,                       
                    }
                )
            
            # Delete the file from the public bucket
            s3_client.delete_object(Bucket=bucket, Key=key)

    except Exception as e: 
        print(e)
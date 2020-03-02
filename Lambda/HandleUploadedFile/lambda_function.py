import boto3
import uuid
from urllib.parse import unquote_plus
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])

            response = s3_client.head_object(Bucket=bucket, Key=key)
            size = response['ContentLength']
            if (size > 10000000):
                print('File too large ({} bytes). Deleting {}'.format(size, key))
                s3_client.delete_object(Bucket=bucket, Key=key)
                continue
            
            contentType = response['ContentType']
            if ("image" not in contentType.lower()):
                print('File is not an image. Deleting {}'.format(key))
            else:
                # Move the file to the non-public images bucket
                s3_client.copy_object(CopySource=bucket + '/' + key, Bucket='wtfthat-images', Key= key)

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
import boto3
import uuid
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            key = unquote_plus(record['s3']['object']['key'])
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('Images')
            uid_str = uuid.uuid4().urn

            response = table.put_item(
                Item = {
                    'Id': uid_str[9:],
                    'OriginalFileName': key.split('-')[1]
                }
            )
    except Exception as e:
        print (e)
import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
import imghdr

s3_client = boto3.client('s3')

def lambda_handler(event, context):
	try:
		for record in event['Records']:
			bucket = record['s3']['bucket']['name']
			key = unquote_plus(record['s3']['object']['key'])
			tmpkey = key.replace('/', '')
			download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
			upload_path = '/tmp/resized-{}'.format(tmpkey)
			s3_client.download_file(bucket, key, download_path)
			statinfo = os.stat(download_path)
			
			if (imghdr.what(download_path) == None):
				print('File is not an image. Deleting {}'.format(statinfo.st_size, key))
				s3.delete_object(Bucket=bucket, Key=key)
				continue

			if (statinfo.st_size < 10000000):
				s3_client.upload_file(upload_path, '{}-images'.format(bucket), key)
			else:
				print('File too large ({} bytes). Deleting {}'.format(statinfo.st_size, key))
				s3.delete_object(Bucket=bucket, Key=key)
	except Exception as e: 
		print(e)
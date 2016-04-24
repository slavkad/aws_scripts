#!/usr/bin/python

import boto3
from datetime import timedelta
from datetime import datetime

import sys, getopt

import time

today=time.strftime("%Y-%m-%d")

env=''

try:
	opts, args = getopt.getopt(sys.argv[1:],"he:",["env="])
except getopt.GetoptError:
	print 'test.py -e <env>'
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print '<script> -e <env>'
		sys.exit()
	elif opt in ("-e", "--env"):
		env = arg

aws_env= 'aws-' + env

session = boto3.Session(profile_name= aws_env)
s3_conn = session.client('s3')
s3 = session.resource('s3')

print """

+==========================================
| """ + aws_env.upper()  + " for " + str(today) + """ 
+==========================================

"""

for bucket in s3.buckets.all():
	
	try: 

		bucket_location = s3_conn.get_bucket_location(
    		Bucket= bucket.name
		)

	except:
		print '{0} - cant connect' .format(bucket.name)

	cw_client = session.client('cloudwatch',region_name= bucket_location['LocationConstraint'])

	cw= cw_client.get_metric_statistics(
		Namespace='AWS/S3',
	 	MetricName='BucketSizeBytes',
	 	StartTime=datetime.utcnow() - timedelta(days=2),
	 	EndTime=datetime.utcnow(), Period=86400,
	 	Statistics=['Sum'],
	 	Unit='Bytes',
	 	Dimensions=[
	 		{'Name':'BucketName', 'Value': bucket.name},
	 		{u'Name': 'StorageType', u'Value': 'StandardStorage'}
	 		]
	 	)
	for dp in cw['Datapoints']:
		print '{0} - {1} - {2:.2f} Bytes - {3:.2f} GB' .format (bucket.name, bucket_location['LocationConstraint'], dp['Sum'], dp['Sum']/1024/1024/1024)
	

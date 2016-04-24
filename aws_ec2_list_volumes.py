#!/usr/bin/python

import boto3
from datetime import timedelta
from datetime import datetime

import sys, getopt

import time

region="us-west-1"

today=time.strftime("%Y-%m-%d")

env=''

try:
	opts, args = getopt.getopt(sys.argv[1:],"he:",["env="])
except getopt.GetoptError:
	print 'aws_ec2_list_volumes.py -e <env>'
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print '<script> -e <env>'
		sys.exit()
	elif opt in ("-e", "--env"):
		env = arg

aws_env= 'aws-' + env

session = boto3.Session(profile_name= aws_env)

ec2_conn = session.client('ec2', region_name=region)
ec2_resource_conn = session.resource('ec2', region_name=region)
cw_client = session.client('cloudwatch',region_name=region)

print """

+==========================================
| """ + aws_env.upper()  + " for " + str(today) + """ 
+==========================================

"""

ec2_volumes  = ec2_resource_conn.volumes.filter(
        Filters=[{'Name': 'status', 'Values': ['available']}],
        MaxResults=1000
    )


for volume in ec2_volumes:
	response = ec2_conn.describe_volumes(VolumeIds=[volume.id])
	for vol_detail in response['Volumes']:
		print '{0} - {1} GB - Created on {2}' .format (volume.id, vol_detail['Size'], vol_detail['CreateTime'])

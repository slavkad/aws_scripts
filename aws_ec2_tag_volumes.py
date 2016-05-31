#!/usr/bin/python

import boto3
from datetime import timedelta
from datetime import datetime

import sys, getopt

import time

region="us-west-1"

today=time.strftime("%Y-%m-%d--%H:%M:%S")

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
instances = ec2_conn.describe_instances()

for each_instance in instances['Reservations']:
	for device in each_instance['Instances'][0]['BlockDeviceMappings']:
		print today + " -- " + each_instance['Instances'][0]['InstanceId'] + " - " + device['Ebs']['VolumeId'] + " " + device['DeviceName']
		volume_id=device['Ebs']['VolumeId']
		name_tag=''
		for tags in each_instance['Instances'][0]['Tags']:
			if tags['Key'] == 'Name':
				name_tag=tags['Value']
		volume = ec2_resource_conn.Volume(volume_id)
		tag = volume.create_tags(
			DryRun=False,
			Tags=[
				{
					'Key': 'ec2-name',
					'Value': name_tag
        		},
				{
					'Key': 'ec2-instance',
					'Value': each_instance['Instances'][0]['InstanceId']
        		},
        		{
					'Key': 'device-name',
					'Value': device['DeviceName']
        		},
        		{
					'Key': 'last-seen',
					'Value': today
        		},
        		]
        	)
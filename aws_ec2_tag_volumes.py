#!/usr/bin/python

import boto3
from datetime import timedelta
from datetime import datetime
import sys, getopt
import time

'''
This script will scan through instances first
determine all volumes attached to it and then tag each of those volumes
with some of the info

instance name
instance id
device name how this volume is mapped on instance
and last seen

if instance gets terminated and volume is left behind,
it will not be "picked up" by this script, as it basis its search on instances (stopped or running)

'''


region="us-west-1"

today=time.strftime("%Y-%m-%d--%H:%M:%S")

env=''
sleep=60
count=0

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
		volume_id=device['Ebs']['VolumeId']
		name_tag=''
		volume_instance_id_tag=''
		volume_name_tag=''
		for tags in each_instance['Instances'][0]['Tags']:
			if tags['Key'] == 'Name':
				name_tag=tags['Value']
		volume = ec2_resource_conn.Volume(volume_id)
		print str(count) + ": " + today + " -- " + name_tag + " --- " + each_instance['Instances'][0]['InstanceId'] + " - " + device['Ebs']['VolumeId'] + " " + device['DeviceName']

		if volume.tags:
			for volume_tags in volume.tags:
				if volume_tags['Key'] == 'ec2-instance':
					volume_instance_id_tag=volume_tags['Value']
				if volume_tags['Key'] == 'Name':
					volume_name_tag=volume_tags['Value']


		if (each_instance['Instances'][0]['InstanceId'] != volume_instance_id_tag) or (volume_name_tag == '') :
			if volume_name_tag == '':
				tag = volume.create_tags(
					DryRun=False,
					Tags=[
						{
							'Key': 'Name',
							'Value': name_tag
		  	      		},
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
				print " key updated with name"
			else:
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
				print " key updated NO name"
		else:
			tag = volume.create_tags(
			DryRun=False,
			Tags=[
   	    	 	{
					'Key': 'last-seen',
					'Value': today
       	 		},
        		]
        	)
			print " date updated "
		count += 1
		if count % 50 == 0:
			print "count is " + str(count) + " sleeping ... Zzzz"
			time.sleep(sleep)

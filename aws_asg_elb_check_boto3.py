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

asg_conn = session.client('autoscaling')
elb_conn = session.client('elb')

asgs = asg_conn.describe_auto_scaling_groups()

print '{0:15}{1:70}{2:30}{3:110}'.format ('InstanceID','ASG','ELB','Description')

for asg in asgs['AutoScalingGroups']:
	for lb in asg['LoadBalancerNames']:
		for instance in asg['Instances']:
			ec2_id=instance['InstanceId']
			instance_elb_health = elb_conn.describe_instance_health(
					LoadBalancerName=lb,
					Instances=[{'InstanceId': str(ec2_id)}]
					)
			if instance_elb_health['InstanceStates'][0]['State'] != "InService":
				print '{0:15}{1:70}{2:30}{3:110}'.format (instance['InstanceId'] , asg['AutoScalingGroupName'], lb, instance_elb_health['InstanceStates'][0]['Description'])

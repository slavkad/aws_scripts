#!/usr/bin/python
import boto.ec2.elb
import os, boto.sts, sys, string, getopt
import boto.ec2.autoscale
import re
import time

aws_region = ""
aws_role_name = ""
aws_role = ""
aws_session_name = ""
aws_role_external_id = ""
fname = "/tmp/ec2_list.txt"

sts = boto.sts.connect_to_region(aws_region)
creds = sts.assume_role(aws_role, aws_session_name, external_id=aws_role_external_id)

# connect to ec2
ec2_conn = boto.ec2.connect_to_region(aws_region,
   aws_access_key_id=creds.credentials.access_key,
   aws_secret_access_key=creds.credentials.secret_key,
   security_token=creds.credentials.session_token)

# open file with IP addresses
with open(fname) as f:
	content= [x.strip() for x in f.readlines()]

print content

instance_internal_ip=content

reservations = ec2_conn.get_all_instances(filters={'instance_id':instance_internal_ip})

instances = [i for r in reservations for i in r.instances]
print instances

for each_instance in instances:
	print each_instance.id + " " + each_instance.private_ip_address + " " + each_instance.tags['Name'] + " " + each_instance.state

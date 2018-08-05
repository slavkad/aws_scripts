#!/usr/bin/python

import boto3
import re
import csv
import sys, getopt

try:
    opts, args = getopt.getopt(sys.argv[1:],"hv:a:r:",["vpc=","account=","region="])
except getopt.GetoptError:
    print 'network_interfaces.py --vpc <vpc_id> --account <aws profile> --region <aws region>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print '<script> -vpc <vpc_id> -account <aws profile>'
        sys.exit()
    elif opt in ("-v", "--vpc"):
        vpc_id = arg
    elif opt in ("-a", "--account"):
        aws_profile = arg
    elif opt in ("-r", "--region"):
        region = arg

session = boto3.Session(profile_name=aws_profile, region_name=region)
client = session.client('ec2')


all_ec2_instances = client.describe_instances(
          Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])

all_network_interfaces = client.describe_network_interfaces(
          Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])

interface_function = 'unknown'
instance_id = ''
ec2_instance_map = {}


for each_ec2_instance in all_ec2_instances['Reservations']:
    ec2_instance_id = each_ec2_instance['Instances'][0]['InstanceId']
    ec2_instance_name = 'NotDetermined'
    try:
        for tags in each_ec2_instance['Instances'][0]['Tags']:
            if tags['Key'] == 'Name':
                ec2_instance_name = tags['Value']
    except:
        ec2_instance_name='NoName'
    ec2_instance_map[ec2_instance_id]=ec2_instance_name

for each_network_interface in all_network_interfaces['NetworkInterfaces']:
    interface_id = each_network_interface['NetworkInterfaceId']
    private_ip = each_network_interface['PrivateIpAddress']

    try:
        if each_network_interface['Attachment']['InstanceId']:
            instance_id = each_network_interface['Attachment']['InstanceId']
    except:
        instance_id = 'nothing'

    # print aws_profile, vpc_id, region, interface_id, instance_id

    if each_network_interface['Description'] == '' :
        interface_function = 'EC2'
        try:
            instance_name = ec2_instance_map[instance_id] + "_" + instance_id
        except:
            instance_name = "notFoundinDict_" + instance_id
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, instance_name, interface_id, private_ip)
    elif "ELB" in each_network_interface['Description']:
        interface_function = 'ELB'
        (crap,elb_name)=each_network_interface['Description'].split(' ')
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, elb_name, interface_id, private_ip)
    elif "Lambda" in each_network_interface['Description']:
        interface_function = 'Lambda'
        (crap,lambda_id)=each_network_interface['Description'].split(': ')
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, lambda_id, interface_id, private_ip)
    elif "RDS" in each_network_interface['Description']:
        interface_function = 'RDS'
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, '', interface_id, private_ip)
    elif 'ElastiCache' in each_network_interface['Description']:
        interface_function = 'ElastiCache'
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, each_network_interface['Description'], interface_id, private_ip)
    elif 'Redshift' in each_network_interface['Description']:
        interface_function = 'Redshift'
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, each_network_interface['Description'], interface_id, private_ip)
    elif 'EFS' in each_network_interface['Description']:
        interface_function = 'EFS'
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, each_network_interface['Description'], interface_id, private_ip)
    elif 'Primary network interface' in each_network_interface['Description']:
        interface_function = 'EC2'
        try:
            instance_name = ec2_instance_map[instance_id] + "_" + instance_id
        except:
            instance_name = instance_id
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, instance_name, interface_id, private_ip)
    elif 'DMS' in each_network_interface['Description']:
        interface_function = 'DMS'
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, '', interface_id, private_ip)
    else:
        interface_function = 'unkown'
        print '"{0}","{1}","{2}","{3}"'.format(interface_function, '', interface_id, private_ip)

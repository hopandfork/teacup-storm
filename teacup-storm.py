'''
Copyright 2016, 2017 Hop and Fork.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

''' This file is currently inteded to test aws and boto3 capabilities. '''
import os
import sys
import boto3
import yaml
from configuration import Configuration

# Global configuration object
config=None

        
''' Creates a session using user-provided custom credentials. '''
def create_session():
    global config
    session = boto3.session.Session(
        aws_access_key_id = config.aws_access_key_id,
        aws_secret_access_key = config.aws_secret_access_key,
        region_name = config.region_name
    )
    return session

def get_ami_id(name):
    global config
    ami_id = None
    if name == "nimbus":
        ami_id = config.nimbus_ami_id
    elif name == "supervisor":
        ami_id = config.supervisor_ami_id
    elif name == "ui":
        ami_id = config.ui_ami_id
    elif name == "zookeeper":
        ami_id = config.zookeeper_ami_id
    return ami_id

''' Starts a single ec2 instance. '''
def start_ec2_instance(session, userdata, securitygroups, name, type, count=1):
    ami_id = get_ami_id(name)            
    ec2 = session.resource('ec2')
    instances = ec2.Subnet(config.subnet_id).create_instances(
        ImageId=ami_id,
        MinCount=count,
        MaxCount=count,
        KeyName=config.key_pair,
        InstanceType=type,
        UserData=userdata,
        SecurityGroupIds=securitygroups,
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': config.volume_size,
                }
            }
        ]
    )
    for instance in instances:
        instance.wait_until_running()
        instance.create_tags(
            Tags=[
                {
                    'Key': 'Name',
                    'Value': name
                }
            ]
        )
        instance.load()
        with open("/etc/hosts", "a") as myfile:
            myfile.write("# teacup storm host\n" + instance.public_ip_address 
                + " " + instance.private_dns_name + "\n")
        print(name + " instance with id " + instance.instance_id + ", " 
              + "private ip " + instance.private_ip_address + " and public ip "
              + instance.public_ip_address + " is " + instance.state["Name"])
    return instances

''' Gets default user data to run on startup. '''
def get_zk_userdata():
    stream = open("./scripts/zookeeper.sh")
    userdata = stream.read()
    stream.close()
    return userdata

def get_storm_userdata():
    stream = open("./scripts/storm.sh")
    userdata = stream.read()
    stream.close()
    return userdata

def start_zk_instance(session):
    global config
    userdata = get_zk_userdata()
    return start_ec2_instance(session, userdata, config.security_groups_zk,
        "zookeeper", config.zookeeper_instance_type)

def start_nimbus_instance(session, zk_instances):
    global config
    userdata = get_storm_userdata()
    zk_ips = ""
    for instance in zk_instances:
        zk_ips += echo_cmd("\'- \"" + instance.private_dns_name + '"\'',
                           "./storm.yaml")
    userdata = userdata.replace("_ZOOKEEPER_SERVERS_\n", zk_ips)
    userdata = userdata.replace("_NIMBUS_SEEDS_", '"127.0.0.1"')
    userdata = userdata.replace("_STORM_SERVICE_", "nimbus")
    userdata = userdata.replace("_SUPERVISOR_PORTS_", "")
    return start_ec2_instance(session, userdata, config.security_groups_ni,
        "nimbus", config.nimbus_instance_type)

def compute_supervisor_ports(slots=4):
    supervisor_ports = "echo 'supervisor.slots.ports:' >> ./storm.yaml\n"
    starting_port = 6700
    for i in range(0, slots):
        port = starting_port + i
        supervisor_ports += "echo '- " + str(port) + "' >> ./storm.yaml\n"
    return supervisor_ports

def start_supervisor_instance(session, zk_instances, nimbus_instances):
    global config
    userdata = get_storm_userdata()
    zk_ips = ""
    for instance in zk_instances:
        zk_ips += echo_cmd("\'- \"" + instance.private_dns_name + '"\'',
                           "./storm.yaml")
    userdata = userdata.replace("_ZOOKEEPER_SERVERS_\n", zk_ips)

    nimbus_ips = ""
    for index, instance in enumerate(nimbus_instances):
        if index > 0:
            nimbus_ips += ", "
        nimbus_ips += '"' + instance.private_dns_name + '"'
    
    supervisor_ports = compute_supervisor_ports(config.slots)
    
    userdata = userdata.replace("_NIMBUS_SEEDS_", nimbus_ips)
    userdata = userdata.replace("_SUPERVISOR_PORTS_", supervisor_ports)
    userdata = userdata.replace("_STORM_SERVICE_", "supervisor")
    return start_ec2_instance(session, userdata, config.security_groups_sv,
        "supervisor", config.supervisor_instance_type, config.supervisors)

def start_ui_instance(session, zk_instances, nimbus_instances):
    global config
    userdata = get_storm_userdata()
    zk_ips = ""
    for instance in zk_instances:
        zk_ips += echo_cmd("\'- \"" + instance.public_ip_address + '"\'',
                           "./storm.yaml")
    userdata = userdata.replace("_ZOOKEEPER_SERVERS_\n", zk_ips)

    nimbus_ips = ""
    for index, instance in enumerate(nimbus_instances):
        if index > 0:
            nimbus_ips += ", "
        nimbus_ips += '"' + instance.public_ip_address + '"'

    userdata = userdata.replace("_NIMBUS_SEEDS_", nimbus_ips)
    userdata = userdata.replace("_STORM_SERVICE_", "ui")
    userdata = userdata.replace("_SUPERVISOR_PORTS_", "")
    return start_ec2_instance(session, userdata, config.security_groups_ui,
        "ui", config.ui_instance_type)

def start_storm_cluster(session):
    zk_instances = start_zk_instance(session)
    nimbus_instances = start_nimbus_instance(session, zk_instances)
    start_supervisor_instance(session, zk_instances, nimbus_instances)
    start_ui_instance(session, zk_instances, nimbus_instances)

def echo_cmd(command, filename):
    return "echo " + command + " >> " + filename + "\n"

def main():
    global config
    config = Configuration()
    session = create_session()
    if os.getuid() != 0:
        print("You should run as root.")
        return -1
    if len(sys.argv) == 1:
            print("Starting storm cluster...")
            start_storm_cluster(session) 
    else:
        print("Usage: teacup-storm.py (no arguments)")
    
if __name__ == "__main__":
    main()

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
def start_ec2_instance(session, userdata, securitygroups, name, count=1):
    ami_id = get_ami_id(name)            
    ec2 = session.resource('ec2')
    instances = ec2.Subnet(config.subnet_id).create_instances(
        ImageId=ami_id,
        MinCount=count,
        MaxCount=count,
        KeyName=config.key_pair,
        InstanceType=config.instance_type,
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

''' Prints instances state change. '''
def print_state_change(response):
    for instance in response:
        iId = instance["InstanceId"]
        curr = instance["CurrentState"]["Name"]
        prev = instance["PreviousState"]["Name"]
        print("Instance with id " + iId + " changed from " + prev + " to " 
              + curr)

''' Returns running instances ids. '''
def get_instances_by_state_name(session, state_name):
    idList = []
    ec2 = session.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    state_name
                ]
            }
        ]
    )
    for instance in instances:
        idList.append(instance.instance_id)

    return idList

''' Terminates all ec2 instances. '''
def terminate_all_ec2_instances(session):
    ec2 = session.resource('ec2')
    
    running_ids = get_instances_by_state_name(session, 'running')
    if len(running_ids):
        running = ec2.instances.filter(InstanceIds=running_ids)
        stop_response = running.stop()
        print_state_change(stopResponse[0]["StoppingInstances"])
    else:
        print("No running instance to stop.")

    stopped_ids = get_instances_by_state_name(session, 'stopped')
    if len(stopped_ids):
        stopped = ec2.instances.filter(InstanceIds=stopped_ids)
        terminate_response = stopped.terminate()  
        print_state_change(terminateResponse[0]["TerminatingInstances"])
    else:
        print("No stopped instances to terminate.")

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
        "zookeeper")

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
        "nimbus")

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
        "supervisor", config.supervisors)

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
        "ui")

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
    if len(sys.argv) > 1 and (sys.argv[1] == "start" or sys.argv[1] == "stop"):
        if sys.argv[1] == "start":
            print("Starting storm cluster...")
            start_storm_cluster(session)
        elif sys.argv[1] == "stop":
            print("Stopping ec2 instances...")
            terminate_all_ec2_instances(session)
    else:
        print("Usage: teacup-storm.py <start|stop>")
    
if __name__ == "__main__":
    main()

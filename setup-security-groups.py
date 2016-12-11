'''
Creates required security groups on EC2 and prints lines to be pasted 
into YAML configuration.
'''

import sys
import boto3
import yaml
from configuration import Configuration

# Global configuration object
config=None

# Needed security groups
group_names = [ 'teacup-storm-ssh', 'teacup-storm-ui', 'teacup-storm-zk', 'teacup-storm-nimbus', 'teacup-storm-sv' ]
security_groups = { name:None for name in group_names}

        
''' Creates a session using user-provided custom credentials. '''
def create_session():
    global config
    session = boto3.session.Session(
        aws_access_key_id = config.aws_access_key_id,
        aws_secret_access_key = config.aws_secret_access_key,
        region_name = config.region_name
    )
    return session

def create_security_group(vpc, name, description=''):
    try:
        return vpc.create_security_group(GroupName=name, Description=description)    
    except boto3.exceptions.botocore.client.ClientError as e:
        print("[ERROR] Failed to create security group '{}' ({})"
                .format(_name, e.response['Error']['Code']))
        exit(2)

def create_zookeeper_sg(vpc):
    sg = create_security_group(vpc, 'teacup-storm-zk', 'Opens ports for ZK')
    sg.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=2181,ToPort=2181)
    sg.authorize_ingress(IpProtocol="udp",CidrIp="0.0.0.0/0",FromPort=2181,ToPort=2181)

def create_nimbus_sg(vpc):
    sg = create_security_group(vpc, 'teacup-storm-nimbus', 'Opens ports for Nimbus')
    sg.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=6627,ToPort=6627)
    sg.authorize_ingress(IpProtocol="udp",CidrIp="0.0.0.0/0",FromPort=6627,ToPort=6627)

def create_supervisor_sg(vpc):
    sg = create_security_group(vpc, 'teacup-storm-sv', 'Opens ports for Supervisor')
    sg.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=6700,ToPort=6703)
    sg.authorize_ingress(IpProtocol="udp",CidrIp="0.0.0.0/0",FromPort=6700,ToPort=6703)

def create_ui_sg(vpc):
    sg = create_security_group(vpc, 'teacup-storm-ui', 'Opens ports for UI')
    sg.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=8080,ToPort=8080)

def create_ssh_sg(vpc):
    sg = create_security_group(vpc, 'teacup-storm-ssh', 'Opens ports for SSH')
    sg.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)

def print_configuration():
    """ Prints lines to be pasted into config.yaml. """
    print("Add following lines to config.yaml")
    print(30*'-')

    _ssh = security_groups['teacup-storm-ssh'].id
    _default = config.default_vpc_security_group
    _ui = security_groups['teacup-storm-ui'].id
    _sv = security_groups['teacup-storm-sv'].id
    _nimbus = security_groups['teacup-storm-nimbus'].id
    _zk = security_groups['teacup-storm-zk'].id

    print('security_groups_zk: ["{}", "{}", "{}"]'.format(_default, _ssh, _zk))
    print('security_groups_ni: ["{}", "{}", "{}"]'.format(_default, _ssh, _nimbus))
    print('security_groups_sv: ["{}", "{}", "{}"]'.format(_default, _ssh, _sv))
    print('security_groups_ui: ["{}", "{}", "{}"]'.format(_default, _ssh, _ui))
    print(30*'-')

def get_group_by_name (vpc, name):
    """ Returns a SecurityGroup given its name. """
    sg = None

    _filters=[{"Name":"group-name", "Values": ["{}".format(name)]}]
    for i in vpc.security_groups.filter(Filters=_filters):
        sg = i

    return sg

def main():
    global config

    config = Configuration()
    session = create_session()
    vpc = session.resource('ec2').Vpc(config.default_vpc)

    # Searches for already existing groups (if any)
    for name in security_groups.keys():
        security_groups[name] = get_group_by_name(vpc, name)
        if security_groups[name] != None:
            print("[WARNING] Security group '{}' already exists (please, rename "
                   "it if you manually created it for a different purpose and "
                   "re-run this tool)".format(name))

    # Creates needed groups
    if security_groups['teacup-storm-zk'] == None:
        security_groups['teacup-storm-zk'] = create_zookeeper_sg(vpc)
    if security_groups['teacup-storm-nimbus'] == None:
        security_groups['teacup-storm-nimbus'] = create_nimbus_sg(vpc)
    if security_groups['teacup-storm-sv'] == None:
        security_groups['teacup-storm-sv'] = create_supervisor_sg(vpc)
    if security_groups['teacup-storm-ssh'] == None:
        security_groups['teacup-storm-ssh'] = create_ssh_sg(vpc)
    if security_groups['teacup-storm-ui'] == None:
        security_groups['teacup-storm-ui'] = create_ui_sg(vpc)

    # Prints configuration to paste into YAML file
    print_configuration()
    
if __name__ == "__main__":
    main()

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
    # TODO configure group

def print_configuration():
    pass
    # TODO

def get_group_by_name (vpc, name):
    sg = None

    filters=[{"Name":"group-name", "Values": ["{}".format(name)]}]
    for i in vpc.security_groups.filter(filters):
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


    # TODO other groups

    # Prints configuration to paste into YAML file
    print_configuration()
    
if __name__ == "__main__":
    main()

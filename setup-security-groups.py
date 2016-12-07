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

        
''' Creates a session using user-provided custom credentials. '''
def create_session():
    global config
    session = boto3.session.Session(
        aws_access_key_id = config.aws_access_key_id,
        aws_secret_access_key = config.aws_secret_access_key,
        region_name = config.region_name
    )
    return session

def create_security_groups(session):
    # TODO
    pass

def main():
    global config
    config = Configuration()
    session = create_session()

    create_security_groups(session)
    
if __name__ == "__main__":
    main()

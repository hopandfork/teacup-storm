'''
This file is currently inteded to test aws and boto3 capabilities.
'''
import boto3
import yaml

''' Creates a session using user-provided custom credentials. '''
def createSession():
    stream = open("config.yaml")
    conf = yaml.load(stream)
    
    session = boto3.session.Session(
        aws_access_key_id=conf["id"],
        aws_secret_access_key=conf["key"],
        region_name=conf["region"]
    )
    return session

''' Prints list of s3 buckets. '''
def printS3Buckets(session):
    s3 = session.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

def main():
    session = createSession()
    printS3Buckets(session)
    
if __name__ == "__main__":
    main()

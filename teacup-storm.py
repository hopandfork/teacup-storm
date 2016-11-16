''' This file is currently inteded to test aws and boto3 capabilities. '''
import boto3
import sys
import yaml

''' Creates a session using user-provided custom credentials. '''
def createSession():
    stream = open("config.yaml")
    conf = yaml.load(stream)
    
    session = boto3.session.Session(
        aws_access_key_id = conf["id"],
        aws_secret_access_key = conf["key"],
        region_name = conf["region"]
    )
    return session

''' Prints list of s3 buckets. '''
def printS3Buckets(session):
    s3 = session.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

''' Starts a single ec2 instance. '''
def startEc2Instance(session):
    ec2 = session.resource('ec2')
    ec2.create_instances(
        ImageId="ami-f3659d9c",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro"
    )

''' Stops a single ec2 instance. '''
def terminateEc2Instance(session):
    ec2 = session.resource('ec2')
    ec2.instances.stop()
    ec2.instances.terminate()  

def main():
    session = createSession()
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            print("Starting ec2 instance...")
            startEc2Instance(session)
        elif sys.argv[1] == "stop":
            print("Stopping ec2 instance...")
            terminateEc2Instance(session)
        else:
            print("Usage: teacup-storm.py <start|stop>")
    else:
        printS3Buckets(session)
    
if __name__ == "__main__":
    main()

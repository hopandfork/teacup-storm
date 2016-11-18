''' This file is currently inteded to test aws and boto3 capabilities. '''
import boto3
import sys
import yaml

''' Global configuration object. '''
global config

class Configuration:
    def __init__(self):
        stream = open("config.yaml")
        conf = yaml.load(stream)
        stream.close()
        self.aws_access_key_id = conf["aws_access_key_id"]
        self.aws_secret_access_key = conf["aws_secret_access_key"]
        self.region_name = conf["region_name"]
        self.key_pair = conf["key_pair"]
        
''' Creates a session using user-provided custom credentials. '''
def createSession():
    global config
    session = boto3.session.Session(
        aws_access_key_id = config.aws_access_key_id,
        aws_secret_access_key = config.aws_secret_access_key,
        region_name = config.region_name
    )
    return session

''' Prints list of s3 buckets. '''
def printS3Buckets(session):
    s3 = session.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

''' Starts a single ec2 instance. '''
def startEc2Instance(session, userdata = ""):
    ec2 = session.resource('ec2')
    response = ec2.create_instances(
        ImageId="ami-f3659d9c",
        MinCount=1,
        MaxCount=1,
        KeyName=config.key_pair,
        InstanceType="t2.micro",
        UserData=userdata,
        SecurityGroupIds=[
            "sg-de1a46b6",
            "sg-fa4ca692"
        ]
    )
    for instance in response:
        print("Status of instance with id " + instance.instance_id + " is " 
            + instance.state["Name"])

''' Prints instances state change. '''
def printStateChange(response):
    for instance in response:
        iId = instance["InstanceId"]
        curr = instance["CurrentState"]["Name"]
        prev = instance["PreviousState"]["Name"]
        print("Instance with id " + iId + " changed from " + prev + " to " 
            + curr)

''' Returns running instances ids. '''
def getInstancesByStateName(session, stateName):
    idList = []
    ec2 = session.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    stateName
                ]
            }
        ]
    )
    for instance in instances:
        idList.append(instance.instance_id)

    return idList

''' Terminates all ec2 instances. '''
def terminateAllEc2Instances(session):
    ec2 = session.resource('ec2')
    
    runningIds = getInstancesByStateName(session, 'running')
    if (len(runningIds)):
        running = ec2.instances.filter(InstanceIds=runningIds)
        stopResponse = running.stop()
        printStateChange(stopResponse[0]["StoppingInstances"])
    else:
        print("No running instance to stop.")

    stoppedIds = getInstancesByStateName(session, 'stopped')
    if (len(stoppedIds)):
        stopped = ec2.instances.filter(InstanceIds=stoppedIds)
        terminateResponse = stopped.terminate()  
        printStateChange(terminateResponse[0]["TerminatingInstances"])
    else:
        print("No stopped instances to terminate.")

''' Gets default user data to run on startup. '''
def getUserdata():
    stream = open("testdata.sh")
    userdata = stream.read()
    stream.close()
    return userdata

def main():
    global config
    config = Configuration()
    session = createSession()
    userdata = getUserdata()
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            print("Starting ec2 instance...")
            startEc2Instance(session, userdata)
        elif sys.argv[1] == "stop":
            print("Stopping ec2 instances...")
            terminateAllEc2Instances(session)
        else:
            print("Usage: teacup-storm.py <start|stop>")
    else:
        printS3Buckets(session)
    
if __name__ == "__main__":
    main()

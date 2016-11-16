'''
This version simply starts and stops machines on AWS.
'''
import boto3
import yaml


def createSession():
    #Read configuration
    stream = open("config.yaml")
    conf = yaml.load(stream)
    ACCESS_KEY = conf["id"]
    SECRET_KEY = conf["key"]
    REGION = conf["region"]
    
    session = boto3.session.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION
    )
    return session

def main():
    # Print list of s3 buckets.
    '''s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION
    )'''
    session = createSession()
    s3 = session.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

if __name__ == "__main__":
    main()

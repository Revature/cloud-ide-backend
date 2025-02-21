# aws.py
import asyncio
import functools
import boto3
from botocore.exceptions import ClientError

###################
# EC2 Functionality
###################

# 'ami-01c42560340a40285' - Ubuntu 24.04 LTS arm64
# 'ami-0991721486ed52a2c' - Ubuntu 24.04 LTS x86_64

async def Create_New_EC2(ImageId='ami-0991721486ed52a2c', InstanceType='t2.medium', InstanceCount=1 ) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.run_instances(
            ImageId=ImageId,
            InstanceType=InstanceType,
            MinCount=InstanceCount,
            MaxCount=InstanceCount
            )
        return response['Instances'][0]['InstanceId']
    except Exception as e:
        return str(e)    


async def Describe_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(
            InstanceIds=[InstanceId]
            )
        return response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp']
    except Exception as e:
        return str(e)


async def Describe_EC2_State(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(
            InstanceIds=[InstanceId]
            )
        return response['Reservations'][0]['Instances'][0]['State']['Name']
    except Exception as e:
        return str(e)


async def Stop_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.stop_instances(
            InstanceIds=[InstanceId]
            )
        return response['StoppingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)   


async def Start_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.start_instances(
            InstanceIds=[InstanceId]
            )
        return response['StartingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)


async def Terminate_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.terminate_instances(
            InstanceIds=[InstanceId]
            )
        return response['TerminatingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)
    

###################
# S3 Functionality
###################

async def Create_New_S3_Bucket(BucketName) -> str:
    s3 = boto3.client('s3')
    try:
        response = s3.create_bucket(
            Bucket=BucketName
            )
        return response['Location']
    except Exception as e:
        return str(e)
    

async def Delete_S3_Bucket(BucketName) -> str:
    s3 = boto3.client('s3')
    try:
        response = s3.delete_bucket(
            Bucket=BucketName
            )
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as e:
        return str(e)
    

async def List_S3_Buckets() -> list[str]:
    s3 = boto3.client('s3')
    try:
        response = s3.list_buckets()
        buckets = []
        for bucket in response['Buckets']:
            buckets.append(bucket['Name'])
        return buckets
    except Exception as e:
        return [str(e)]


async def List_S3_Objects(BucketName) -> list[str]:
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(
           Bucket=BucketName
            )
        objects = []
        for obj in response['Contents']:
            objects.append(obj['Key'])
        return objects
    except Exception as e:
        return [str(e)]


async def Put_S3_Object(BucketName, ObjectName, ObjectData) -> str:
    s3 = boto3.client('s3')
    try:
        response = s3.put_object(
            Bucket=BucketName,
            Key=ObjectName,
            Body=ObjectData
            )
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as e:
        return str(e)


async def Get_S3_Object(BucketName, ObjectName) -> object:
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(
            Bucket=BucketName,
            Key=ObjectName
            )
        return response['Body'].read()
    except Exception as e:
        return str(e)


async def Delete_S3_Objects(BucketName, ObjectNames) -> str:
    s3 = boto3.client('s3')
    for obj in ObjectNames:
        try:
            response = s3.delete_object(
                Bucket=BucketName,
                Key=obj
                )
            return
        except Exception as e:
            return str(e)
# aws.py
import asyncio
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

###################
# EC2 Functionality
###################

# We can create or terminate vms in batches with the sdk, but I'd recommend that we stick to one at a time for now. If we need to scale, it can be done later, but managing multiple instances across availability zones and regions can lead to inconsistencies, since the termination requests are idempotent by AZ.

async def Create_New_EC2(ImageId='XXXXXXXXXXXX', InstanceType='t2.medium', InstanceCount=1 ) -> str:
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


# Describing the instance will let us gather the ip addresses. Not sure if we want v4 or v6, or if we'll set up an elastic pool or something to help manage. For now I'm pulling individual IPv4, but we can scale this to gather blocks for a list of vms, or swap to v6s if we need to.

async def Describe_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(
            InstanceIds=[InstanceId]
            )
        return response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp']
    except Exception as e:
        return str(e)


# Stopping a vm will produce returns almost the same as a terminiation, so we can monitor state the same way. We haven't talked about hibernating vms, but it's an option if we want to save state and resources, but it's not a default option in the sdk. We shouldn't get charged for stopped or hibernated instances, but if we have volumes attached we'll still be charged or them as if they were running.

async def Stop_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.stop_instances(
            InstanceIds=[InstanceId]
            )
        return response['StoppingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)   


# Start is... well, a startup. Nothing should have changed, but we should probably run a healthcheck on the vm and the runner on it once it's back up, as well as geting the connection details in the event that the IP gets rotated to a new VM while an instance is stopped.

async def Start_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.start_instances(
            InstanceIds=[InstanceId]
            )
        return response['StartingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)


# Termination is idempotent, so multiple calls will return sucessful responses. We can leverage this to monitor shut downs, as a return will give us the instance id, current state, and previous state (from last state change). We should be able to repeat the request to monitor the progress from 'running'/'stopped' to 'shutting-down' to 'terminated'. We may also see 'pending' if the instance is still initializing, but otherwise it can give us a rough progress report if we want to log from here.

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
    try:
        response = s3.create_bucket(
            Bucket=BucketName
            )
        return response['Location']
    except Exception as e:
        return str(e)
    

async def Delete_S3_Bucket(BucketName) -> str:
    try:
        response = s3.delete_bucket(
            Bucket=BucketName
            )
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as e:
        return str(e)
    

async def List_S3_Buckets() -> list[str]:
    try:
        response = s3.list_buckets()
        buckets = []
        for bucket in response['Buckets']:
            buckets.append(bucket['Name'])
        return buckets
    except Exception as e:
        return [str(e)]


# Listing objects may get messy if there are a lot of objects. The sdk is built to handle 1000 objects at a response, with counts for pagination if we need ALL of the objects. I can add that to this method, but I wasn't sure what we were picturing for the scale here.
async def List_S3_Objects(BucketName) -> list[str]:
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


# Putting objects is both create and update. Puts are never partial, so any metadata change must include the entire object to update

async def Put_S3_Object(BucketName, ObjectName, ObjectData) -> str:
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
    try:
        response = s3.get_object(
            Bucket=BucketName,
            Key=ObjectName
            )
        return response['Body'].read()
    except Exception as e:
        return str(e)


async def Delete_S3_Objects(BucketName, ObjectNames) -> str:
    for obj in ObjectNames:
        try:
            response = s3.delete_object(
                Bucket=BucketName,
                Key=obj
                )
            return
        except Exception as e:
            return str(e)

# async def main():
#     print('Running...')
#     res = await Get_S3_Object('revature-dev-01092022','batch_curriculum_v2_contents/0ea30ce73ff6dfeca0878c07cfc9474a.txt')
#     print(res)

# asyncio.run(main())

# 'batch_curriculum_v2_contents/0ea30ce73ff6dfeca0878c07cfc9474a.txt'
# 'revature-dev-01092022'

# This is a synchronous function that will block until the instance is running. We can use this to wait for the instance to be running before we update the runner's state in the database.
    
def wait_for_instance_running(instance_id: str, region: str = "us-west-2") -> None:
    ec2 = boto3.client("ec2", region_name=region)
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])
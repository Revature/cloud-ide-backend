# aws.py
import boto3
import datetime
import paramiko
from io import StringIO


###################
# Keypair Functionality
###################

# Create_New_Keypair() creates a new keypair and returns the private key and keypair id as a dictionary
async def Create_New_Keypair() -> dict:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.create_key_pair(
            KeyName="Keypair-" + datetime.datetime.now().strftime("%Y-%m-%d")
            )
        return {'PrimaryKey':response['KeyMaterial'], 'KeyPairId':response['KeyPairId']}
    except Exception as e:
        return str(e)


async def Delete_Keypair(KeyId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.delete_key_pair(
            KeyPairId=KeyId
            )
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as e:
        return str(e)


# Describe_KeyPairId() returns the keypair id of the keypair with the given KeyName.
async def Describe_KeyPairId(KeyName) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_key_pairs(
            KeyNames=[KeyName]
            )
        return response['KeyPairs'][0]['KeyPairId']
    except Exception as e:
        return str(e)
    

# Describe_KeyName() returns the name of the keypair with the given KeyId. 
async def Describe_KeyName(KeyPairId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_key_pairs(
            KeyPairIds=[KeyPairId]
            )
        return response['KeyPairs'][0]['KeyName']
    except Exception as e:
        return str(e)
    

###################
# EC2 Functionality
###################

# 'ami-01c42560340a40285' - Ubuntu 24.04 LTS arm64
# 'ami-0991721486ed52a2c' - Ubuntu 24.04 LTS x86_64

async def Create_New_EC2(KeyName, ImageId='ami-0991721486ed52a2c', InstanceType='t2.medium', InstanceCount=1, SecurityGroups=['sg-0f1d1e7f0e5d8936f']) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.run_instances(
            ImageId=ImageId,
            InstanceType=InstanceType,
            MinCount=InstanceCount,
            MaxCount=InstanceCount,
            KeyName=KeyName,
            SecurityGroupIds=SecurityGroups,
            TagSpecifications=[ 
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        { 'Key': 'Name', 'Value': 'Cloud-IDE'},
                    ]
                }
            ]
        )
        return response['Instances'][0]['InstanceId']
    except Exception as e:
        return str(e)    


# Describe_EC2() returns the public IP address of the EC2 instance with the given InstanceId.
async def Describe_EC2(InstanceId) -> str:
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(
            InstanceIds=[InstanceId]
            )
        return response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp']
    except Exception as e:
        return str(e)


# Describe_EC2_State() returns the state of the EC2 instance with the given InstanceId.
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
    
def wait_for_instance_running(instance_id: str, region: str = "us-west-2") -> None:
    ec2 = boto3.client("ec2", region_name=region)
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])

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


###################
# SSH Functionality
###################

async def SSH_Script(IP, Key, Script, Username = 'ubuntu') -> str:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    keyfile = StringIO(Key)
    private_key = paramiko.RSAKey.from_private_key(keyfile)

    try:
        ssh.connect(hostname=IP, username=Username, pkey=private_key)
        stdin, stdout, stderr = ssh.exec_command(Script)
        output = stdout.read().decode()
        error = stderr.read().decode()

    except Exception as e:
        return str(e), error
    
    finally:
        ssh.close()

    return output, error
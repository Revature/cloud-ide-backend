# aws.py
import datetime
from io import StringIO
import boto3
import paramiko

###################
# Keypair Functionality
###################

async def Create_New_Keypair(KeyName: str) -> dict[str, str]:
    """
    Create a new keypair using the provided KeyName.
    Returns a dictionary with the private key and keypair id.
    Example: {'PrimaryKey': <private key>, 'KeyPairId': <keypair id>}
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.create_key_pair(
            KeyName=KeyName
        )
        return {'PrimaryKey': response['KeyMaterial'], 'KeyPairId': response['KeyPairId']}
    except Exception as e:
        return str(e)


async def Delete_Keypair(KeyId) -> str:
    """
    Delete the keypair with the given KeyId.
    Returns the HTTP status code as a string.
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.delete_key_pair(
            KeyPairId=KeyId
            )
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as e:
        return str(e)


async def Describe_KeyPairId(KeyName) -> str:
    """
    Describe the keypair with the given KeyName.
    Returns the KeyPairId as a string.
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_key_pairs(
            KeyNames=[KeyName]
            )
        return response['KeyPairs'][0]['KeyPairId']
    except Exception as e:
        return str(e)


async def Describe_KeyName(KeyPairId) -> str:
    """
    Describe the keypair with the given KeyPairId.
    Returns the KeyName as a string.
    """
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


async def Create_New_EC2(KeyName, ImageId='ami-0bbfffa970b0280da', InstanceType='t2.medium', InstanceCount=1, SecurityGroups=['sg-0f1d1e7f0e5d8936f']) -> str:
#async def Create_New_EC2(ImageId='ami-0bbfffa970b0280da', InstanceType='t2.medium', InstanceCount=1, SecurityGroups=['sg-0f1d1e7f0e5d8936f']) -> str:
    """
    Create a new EC2 instance.
    Returns the InstanceId as a string.
    """
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
                        { 'Key': 'Name', 'Value': 'Ashoka-Testing'},
                    ]
                }
            ]
        )
        return response['Instances'][0]['InstanceId']
    except Exception as e:
        return str(e)


# Future Work: Terminate multiple instances at once -> InstanceId -> InstanceIds
async def Describe_EC2(InstanceId) -> str:
    """
    Describe the EC2 instance with the given InstanceId.
    Returns the public IP address as a string.
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(
            InstanceIds=[InstanceId]
            )
        return response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp']
    except Exception as e:
        return str(e)


# Future Work: Terminate multiple instances at once -> InstanceId -> InstanceIds
async def Describe_EC2_State(InstanceId) -> str:
    """
    Describe the state of the EC2 instance with the given InstanceId.
    Returns the state as a string.
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(
            InstanceIds=[InstanceId]
            )
        return response['Reservations'][0]['Instances'][0]['State']['Name']
    except Exception as e:
        return str(e)


# Future Work: Terminate multiple instances at once -> InstanceId -> InstanceIds
async def Stop_EC2(InstanceId) -> str:
    """
    Stop the EC2 instance with the given InstanceId.
    Returns the state as a string.
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.stop_instances(
            InstanceIds=[InstanceId]
            )
        return response['StoppingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)


# Future Work: Terminate multiple instances at once -> InstanceId -> InstanceIds
async def Start_EC2(InstanceId) -> str:
    """
    Start the EC2 instance with the given InstanceId.
    Returns the state as a string.
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.start_instances(
            InstanceIds=[InstanceId]
            )
        return response['StartingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)


# Future Work: Add a check to see if the instance is already terminated
# Future Work: Terminate multiple instances at once -> InstanceId -> InstanceIds
async def Terminate_EC2(InstanceId) -> str:
    """
    Terminate the EC2 instance with the given InstanceId.
    Returns the state as a string.
    """
    ec2 = boto3.client('ec2')
    try:
        response = ec2.terminate_instances(
            InstanceIds=[InstanceId]
            )
        return response['TerminatingInstances'][0]['CurrentState']['Name']
    except Exception as e:
        return str(e)


def wait_for_instance_running(instance_id: str, region: str = "us-west-2") -> None:
    """
    Wait for the EC2 instance with the given instance_id to be in the running state.
    """
    ec2 = boto3.client("ec2", region_name=region)
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])


###################
# S3 Functionality
###################


async def Create_New_S3_Bucket(BucketName) -> str:
    """
    Create a new S3 bucket with the given BucketName.
    Returns the location as a string.
    """
    s3 = boto3.client('s3')
    try:
        response = s3.create_bucket(
            Bucket=BucketName
            )
        return response['Location']
    except Exception as e:
        return str(e)


async def Delete_S3_Bucket(BucketName) -> str:
    """
    Delete the S3 bucket with the given BucketName.
    Returns the HTTP status code as a string.
    """
    s3 = boto3.client('s3')
    try:
        response = s3.delete_bucket(
            Bucket=BucketName
            )
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as e:
        return str(e)


async def List_S3_Buckets() -> list[str]:
    """
    List all S3 buckets in the default region.
    Returns a list of bucket names as strings.
    """
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
    """
    List all objects in the S3 bucket with the given BucketName.
    Returns a list of object names as strings.
    """
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
    """
    Create or update the object with the given ObjectName and ObjectData into the S3 bucket with the given BucketName.
    Returns the HTTP status code as a string.
    """
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
    """
    Get the object with the given ObjectName from the S3 bucket with the given BucketName.
    Returns the object data as a bytes object.
    """
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
    """
    Delete the objects with the given ObjectNames from the S3 bucket with the given BucketName.
    Returns the HTTP status code as a string.
    """
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


async def SSH_Script(IP, Key, Script, Username='ubuntu') -> dict[str, str]:
    """
    Run the Script on the remote machine with the given IP address.
    Returns the output and error as a dictionary of strings.
    {'Output': value, 'Error': value}
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    keyfile = StringIO(Key)
    private_key = paramiko.RSAKey.from_private_key(keyfile)
    
    print(f"[DEBUG] SSH_Script called with IP: {IP}, Username: {Username}")
    print(f"[DEBUG] Script to execute: {Script}")

    output = ""
    error = ""
    try:
        print("[DEBUG] Connecting to SSH...")
        ssh.connect(hostname=IP, username=Username, pkey=private_key, timeout=30)
        print("[DEBUG] SSH connection established.")

        # Execute a test echo command to verify connectivity.
        test_cmd = "echo 'Test Echo: SSH Connection Successful'"
        print(f"[DEBUG] Executing test command: {test_cmd}")
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        test_output = stdout.read().decode().strip()
        test_error = stderr.read().decode().strip()
        print(f"[DEBUG] Test command output: {test_output}")
        if test_error:
            print(f"[DEBUG] Test command error: {test_error}")

        # Execute the main script.
        print("[DEBUG] Executing main script...")
        stdin, stdout, stderr = ssh.exec_command(Script)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(f"[DEBUG] Main script output: {output}")
        if error:
            print(f"[DEBUG] Main script error: {error}")
    except Exception as e:
        print(f"[ERROR] Exception during SSH execution: {e}")
        return {'Output': str(e), 'Error': error}
    finally:
        print("[DEBUG] Closing SSH connection.")
        ssh.close()

    return {'Output': output, 'Error': error}

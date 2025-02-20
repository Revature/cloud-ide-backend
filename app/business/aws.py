# aws.py

import boto3

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
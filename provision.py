import boto3
from botocore.exceptions import ClientError
import time

'''
Original incantation for starting and stopping EC2 was from the documentation:
https://aws.amazon.com/premiumsupport/knowledge-center/start-stop-lambda-cloudwatch/

Starting and stopping RDS is from:
https://stackoverflow.com/questions/44738071/boto3-start-stop-rds-instance-with-aws-lambda

Allocating/releasing elastic IP addresses is from:
https://boto3.readthedocs.io/en/latest/guide/ec2-example-elastic-ip-addresses.html
'''


def lambda_handler(event, context):
    '''

    :param event: must contain 'mode' (start|stop), 'region' ('us-east-1'), 'ec2_instance'
    :param context:
    :return:
    '''
    mode = event['mode']
    # the region instances are in without specifying Availability Zone; e.g., 'us-east-1'
    region = event['region']

    #ec2 instance ex. ['X-XXXXXXXX', 'X-XXXXXXXX']
    ec2_instance = event['ec2_instance']
    ec2 = boto3.client('ec2', region_name=region)

    rds_instance = event['rds_instance']
    rds = boto3.client('rds')

    if mode == 'start':
        start(ec2, ec2_instance, rds, rds_instance)
    elif mode == 'stop':
        stop(ec2, ec2_instance, rds, rds_instance)
    else:
        print("Must specify a mode.")
        exit(1)

    return 0

def start(ec2, ec2_instance, rds, rds_instance):
    print("Starting up soup")

    print(f"Starting ec2 instance {ec2_instance}")
    ec2.start_instances(InstanceIds=[ec2_instance])
    print(f"Started ec2 instance {ec2_instance}")

    print(f"Starting rds instance {rds_instance}")
    rds.start_db_instance(DBInstanceIdentifier=rds_instance)
    print(f"Starting rds instance {rds_instance}")

    print(f"Allocating EIP address to EC2 instance {ec2_instance}")
    try:
        wait_ec2_target_state(ec2, ec2_instance, "running")

        allocation = ec2.allocate_address(Domain='vpc')
        response = ec2.associate_address(AllocationId=allocation['AllocationId'],
                                         InstanceId=ec2_instance)
        print(response)
        print(f"Allocated EIP address {allocation} to EC2 instance {ec2_instance}")
    except ClientError as e:
        print(e)
        exit(1)

    print("successfully finished starting up soup")

def stop(ec2, ec2_instance, rds, rds_instance):
    print("stopping soup")

    print(f"Stopping ec2 instance {ec2_instance}")
    ec2.stop_instances(InstanceIds=[ec2_instance])
    print(f"Stopped ec2 instance {ec2_instance}")

    wait_ec2_target_state(ec2, ec2_instance, "stopped")

    print(f"Releasing EIP address from EC2 instance {ec2_instance}")
    try:
        allocations = ec2.describe_addresses()
        if len(allocations['Addresses']) != 1:
            print("wrong number of ip allocations returned")
            exit(1)
        association_id = allocations['Addresses'][0]['AssociationId']
        ec2.disassociate_address(AssociationId=association_id)
        allocation_id = allocations['Addresses'][0]['AllocationId']
        ec2.release_address(AllocationId=allocation_id)
        print(f"Released EIP address {allocation_id} from EC2 instance {ec2_instance}")
    except ClientError as e:
        print(e)
        exit(1)

    print(f"Stopping rds instance {rds_instance}")
    rds.stop_db_instance(DBInstanceIdentifier=rds_instance)
    print(f"Stopped rds instance {rds_instance}")

    print("successfully finished stopping soup")

def wait_ec2_target_state(ec2, ec2_instance, target_state):
    for i in range(1, 11):
        print(f"Attempt {i} checking ec2 state")
        response = ec2.describe_instance_status(InstanceIds=[ec2_instance], IncludeAllInstances=True)
        instance_states = response['InstanceStatuses']
        if len(instance_states) != 1:
            print("wrong number of instances returned")
            exit(1)
        state = instance_states[0]['InstanceState']['Name']
        id = instance_states[0]['InstanceId']
        print(f"Instance {id} detected as {state}")
        if id == ec2_instance and state == target_state:
            break
        time.sleep(5.0)
    else:
        print(f"ec2 instance {ec2_instance} did not reach target state {target_state}")
        exit(1)
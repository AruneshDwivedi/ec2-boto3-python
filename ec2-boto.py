import boto3

# Region
region = "ap-southeast-2"

# Create EC2 client
ec2 = boto3.client('ec2', region_name=region)

# Instance configuration
image_id = "ami-0ba8d27d35e9915fb"
instance_type = "t2.2xlarge"
key_name = "my-login"
security_group_ids = ["sg-0e4d813ab0f821b1e"]
subnet_id = "subnet-0bc5e7f9d0755dbbf"

# Docker auto-install + app deployment script (runs when EC2 boots)
user_data_script = """#!/bin/bash
apt update -y
apt install docker.io -y
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Deploy application automatically
docker pull nginx
docker run -d -p 80:80 nginx
"""

# Launch EC2 instance
response = ec2.run_instances(
    ImageId=image_id,
    InstanceType=instance_type,
    KeyName=key_name,
    SecurityGroupIds=security_group_ids,
    SubnetId=subnet_id,
    MinCount=1,
    MaxCount=1,
    UserData=user_data_script,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'ec2-boto3-created'}
            ]
        }
    ]
)

# Extract Instance ID
instance_id = response['Instances'][0]['InstanceId']
print(f"Instance launched: {instance_id}")

# Wait until instance is running
print("Waiting for instance to enter running state...")
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])

# Fetch instance details
instance_desc = ec2.describe_instances(InstanceIds=[instance_id])
instance = instance_desc['Reservations'][0]['Instances'][0]

public_ip = instance.get('PublicIpAddress', 'N/A')
private_ip = instance.get('PrivateIpAddress', 'N/A')
public_dns = instance.get('PublicDnsName', 'N/A')

print("\nInstance Ready!")
print(f"Instance ID: {instance_id}")
print(f"Public IP: {public_ip}")
print(f"Private IP: {private_ip}")
print(f"Public DNS: {public_dns}")
print(f"Open in browser: http://{public_ip}")

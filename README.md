# teacup-storm
Apache Storm deploy on EC2 made easy.

## Dependencies

- boto3
- pyyaml

## AWS requirements

1. An AWS account :-)
2. An AWS Access Key
3. An AMI for launching EC2 instances including Java 7 and Python 2.6.6
4. A default VPC, with a default subnet and a default Security Group
5. (A bunch of Security Groups for the Storm cluster: you can easily setup them
		using `setup-security-groups.py`)

## Configuration

Create a `config.yaml` configuration file starting from `config.example.yaml`.

**If you need to setup required Security Groups:** prepare your configuration file
entering all required settings (keep example data for the Storm cluster security groups). 
Then, run:

	python setup-security-groups.py

and paste generated lines into `config.yaml`.

Here is a list of supported configuration options:

- `region_name`: AWS region to use
- `aws_access_key_id`: ID of your AWS Access Key
- `aws_secret_access_key`: your AWS secret Access Key
- `key_pair`: EC2 keypair to use
- `default_vpc`: ID of your default VPC
- `default_vpc_security_group`: ID of default security group in the VPC
- `security_groups_zk`: list of Security Group to use on ZooKeeper node(s)
- `security_groups_ni`: list of Security Group to use on Nimbus node(s)
- `security_groups_sv`: list of Security Group to use on Supervisor node(s)
- `security_groups_ui`: list of Security Group to use on UI node(s)
- `supervisors`: (optional) number of Supervisor nodes to run (default=1)
- `slots`: (optional) number of workers to run on each Supervisor node (default=4)
- `default_ami_id`: ID of default AMI use for launched instances
- `nimbus_ami_id`: (optional) ID of specific AMI to use for Nimbus instance(s)
- `supervisor_ami_id`: (optional) ID of specific AMI to use for Supervisor instance(s)
- `ui_ami_id`: (optional) ID of specific AMI to use for UI instance(s)
- `zookeeper_ami_id`: (optional) ID of specific AMI to use for ZooKeeper instance(s)

## Usage

	python teacup-storm.py



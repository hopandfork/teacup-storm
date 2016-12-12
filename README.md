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

## Usage

	python teacup-storm.py start
	python teacup-storm.py stop



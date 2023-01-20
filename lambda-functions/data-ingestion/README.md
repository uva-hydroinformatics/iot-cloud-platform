# Data ingestion lambda function
This lambda function queries sensor uplink data from The Things Network storage integration and stores it in a S3 bucket as csv files.

- Python files are available in the deployment-package folder
- flood-warning-data-parsing-and-ingestion is the AWS-SAM file for this function (IAM Role information was omitted)
- ttn-to-s3-query-every-hour-CloudFormation-Template is the cloud formation file for the triggering event for this lambda function (Target information was omitted)


# Initial setup

- Create an S3 bucket to store sensor data
- Create a lambda function with Python 3.9 runtime environment
- Add standard AWS lambda layer AWSSDKPandas-Python39
- Setup the role for your lambda function with authorization to read/write to your target S3 bucket
- Upload python scripts from the deployment-package folder to your lambda function
- Update the configurations.py file with TTN application names and keys
- Update S3 bucket_name variable in lambda_function.py if needed 
- Add and configure a lambda function trigger (EventBridge -> schedule expression = rate(1 hour)) 


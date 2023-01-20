# API data retrieval lambda function
This lambda function is called when an authorized GET request is received by the API and returns requested sensor data.

- Python files are available in the deployment-package folder
- data-download-api is the AWS-SAM file for this function (IAM Role information was omitted)


# Initial setup

- Create and configure your API with the GET method
- Create a lambda function with Python 3.9 runtime environment
- Add standard AWS lambda layer AWSSDKPandas-Python39
- Update the TTN application names and s3 bucket name in the lambda function
- Setup the role for your lambda function with authorization to read from your target S3 bucket
- Upload python scripts from the deployment-package folder to your lambda function


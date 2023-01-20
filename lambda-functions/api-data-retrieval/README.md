# API data retrieval lambda function
This lambda function is called when an authorized GET request is received by the API and returns requested sensor data.

- Python files are available in the deployment-package folder
- data-download-api is the AWS-SAM file for this function (IAM Role information was omitted)


# Initial setup

- Create and configure your API with the GET method
- Create a lambda function with Python 3.9 runtime environment
- Update the TTN application names and s3 bucket name in the lambda function



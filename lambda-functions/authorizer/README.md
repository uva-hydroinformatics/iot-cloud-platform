# Authorizer lambda function
This lambda function is called for every gateway API request and checks if the authorization token matches the key string.

- Python files are available in the deployment-package folder
- api-authorizer is the AWS-SAM file for this function (IAM Role information was omitted)


# Initial setup

- Create and configure your API with the GET method
- Create a lambda function with Python 3.9 runtime environment
- Update the Key string, the user ID string and the GET method ARN in the lambda function



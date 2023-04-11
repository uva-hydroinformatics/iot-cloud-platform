# API and SWAGGER documentation website
This API allows for programmatic access of sensor data

# Initial setup (API Gateway)

- Create and configure the AWS API gateway as described in the YAML file located in the api-swagger-yaml folder
- Update the fields with ?????????? with the respective app parameters (host, authorizer lambda function, etc)
- Make sure the get request is configured to call the lambda function in the /lambda-functions/api-data-retrieval folder 


# Initial setup (API website)

- Create a S3 bucket to host the static website and make it public
- Copy Swagger UI dist files from https://github.com/swagger-api/swagger-ui/tree/master/dist to the created S3 bucket
- Add the files swagger-initializer.js and spec.js from api-website folder to the S3 bucket
- Update the API endpoint https address marked as ?????????? with your AWS API gateway endpoint address

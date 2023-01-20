# - Replace ??????Token?????? with a string to be used as the API access key 
# - Replace ??ID?? with an user ID associated with this authorization event
# - Replace arn:aws:execute-api:?????????:????????? with the method request ARN in the Gateway API (replace the deployment stage with * to enable authorizer to work in any stage)

def lambda_handler(event, context):
    
    if event['authorizationToken'] == '??????Token??????':
        auth = 'Allow'
    else:
        auth = 'Deny'
    
    #3 - Construct and return the response
    authResponse = { "principalId": "??ID??", "policyDocument": { "Version": "2012-10-17", "Statement": [{"Action": "execute-api:Invoke", "Resource": ["arn:aws:execute-api:?????????:?????????"], "Effect": auth}] }}
    return authResponse
    
    
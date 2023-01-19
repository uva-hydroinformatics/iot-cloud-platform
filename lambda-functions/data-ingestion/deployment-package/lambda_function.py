import json
import boto3
from datetime import datetime
from io import StringIO
from http_get import get_data
from parse_response import parse_response
from configurations import ttn_query_list

def lambda_handler(event, context):
    
    bucket_name = 'flood-warning-system-s3bucket'
    request_interval = '65m' 
  
    for ttn_query in ttn_query_list:
        timestamp = datetime.now()
        ttn_response = get_data(ttn_query['application'], ttn_query['key'], last=request_interval)
        
        if ttn_response:
            parsed_df = parse_response(ttn_response)
        else:
            continue
        
        request_date = timestamp.strftime('%Y%m%d')
        hour_min_sec = timestamp.strftime('%H%M%S')
        object_filename = '{}/{}/{}/{}.csv'.format('SensorData', ttn_query['application'], request_date, hour_min_sec)

        
        csv_buffer = StringIO()
        parsed_df.to_csv(csv_buffer)
        
        s3_resource = boto3.resource('s3')
        s3_resource.Object(bucket_name, object_filename).put(Body=csv_buffer.getvalue())

    
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda function executed successfully!')
    }
    

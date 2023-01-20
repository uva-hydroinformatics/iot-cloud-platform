# - Replace ???BUCKET_NAME??? with the S3 bucket name where the sensor data is stored
# - Replace '???TTN_APP???' with the TTN application name as needed

import json
import pandas as pd
import boto3
from io import StringIO

def queryS3(ttn_application,record_day):


        bucket_name = '???BUCKET_NAME???'

        s3 = boto3.client('s3')
        prefix = 'SensorData/'+ttn_application+'/'+record_day
        objects = s3.list_objects(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' not in objects:
                print('Warning: No records labeled {} found for TTN application {}!'.format(record_day,ttn_application))
                return None
        df_list = []
        for object in objects['Contents']:
                csv_string = s3.get_object(Bucket=bucket_name, Key=object['Key'])['Body'].read().decode('utf-8')
                df = pd.read_csv(StringIO(csv_string))
                df['received_at'] = pd.to_datetime(df['received_at'])
                df = df.set_index('received_at')
                df_list.append(df)

        data = pd.concat(df_list)

        return data



def lambda_handler(event, context):
    
    all_ttn_applications = ('???TTN_APP???', '???TTN_APP???', '???TTN_APP???') 

    max_days = 90
    request_time = pd.Timestamp.now()
    request_parameters = event['queryStringParameters']
    
    try:

        if "application" in request_parameters:
            ttn_applications = request_parameters["application"].split(',')
        else:
            ttn_applications = all_ttn_applications  
            
        if "device_id" in request_parameters:
            device_id = int(request_parameters["device_id"])
        else:
            device_id = None
            
        if "start_date" in request_parameters:
            start_date = pd.to_datetime(request_parameters["start_date"], format="%Y-%m-%d", errors='ignore')
        else:
            start_date = None
            
        if "end_date" in request_parameters:
            end_date = pd.to_datetime(request_parameters["end_date"], format="%Y-%m-%d", errors='ignore')
        else:
            end_date = None
            
        if "last" in request_parameters:
            last = pd.Timedelta(request_parameters["last"])
        else:
            last = None
            
    except:
        return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps("Parameters don't match expected format."),
        "isBase64Encoded": False
    }

        
    
    if last:
        requested_days = pd.date_range(request_time-last, request_time)
    else:    
        if start_date and end_date:
            requested_days = pd.date_range(start_date, end_date)
        elif start_date and (end_date is None):
            requested_days = (start_date,)
        elif end_date and (start_date is None):
            requested_days = (end_date,)
        else:
            requested_days = (request_time,)
            
        
    if len(requested_days)> max_days:
        requested_days = requested_days[:10]
    
    df_list = []    
    for ttn_application in ttn_applications:
        for requested_day in requested_days:
            df = queryS3(ttn_application,requested_day.strftime("%Y%m%d"))
            df_list.append(df)
            
    data = pd.concat(df_list)
    
    if device_id:
        data = data.loc[data["device_id"]==device_id]
        
    
    result = data.to_json(orient="split")

    parsed = json.loads(result)

    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': json.dumps(parsed),
        "isBase64Encoded": False
    }

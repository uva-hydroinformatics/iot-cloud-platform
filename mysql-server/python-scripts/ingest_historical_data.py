
import json
import pandas as pd
import boto3
from io import StringIO
import pymysql
import MySQL_parameters
from TTN_parameters import ttn_app_list
from math import isnan

def queryS3(ttn_application,record_day):

        s3 = boto3.client('s3')
        prefix = 'SensorData/'+ttn_application+'/'+record_day
        bucket_name = 'flood-warning-system-s3bucket'
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

def ingestMySQL(df, ttn_application):

        if df is None:
                print('Warning: No data to ingest!')
                return None

        username = MySQL_parameters.username 
        password = MySQL_parameters.password 
        db_name = MySQL_parameters.db_name 

        con = pymysql.connect(host='localhost', user=username, password=password, database=db_name,charset='utf8mb4',unix_socket="/opt/bitnami/mysql/tmp/mysql.sock",cursorclass = pymysql.cursors.DictCursor)

        with con.cursor() as cur:

                for index, row in df.iterrows():

                        Received_at = index.strftime('%Y-%m-%d %H:%M:%S')


                        Device_ID = int(row['device_id'])
                        Device_model = ttn_application
                        Last_battery = row['battery_voltage_value']
                        Last_activity = Received_at
                        sql_query_Devices = "INSERT INTO `FloodWarningDB`.`Devices` (Device_ID, Device_model, Last_battery, Last_activity) VALUES('{}', '{}', {}, '{}') ON DUPLICATE KEY UPDATE Last_battery={}, Last_activity='{}';".format(Device_ID, Device_model, Last_battery, Last_activity,Last_battery, Last_activity)
                        cur.execute(sql_query_Devices)
                        con.commit()

                        Location_ID = str(Device_ID)+'@'+row['metadata_gateway_ids_gateway_id']

                        try:
                                Latitude = float(row['metadata_location_latitude'])
                                Longitude = float(row['metadata_location_longitude'])
                                Altitude = float(row['metadata_location_altitude'])
                                if isnan(Latitude):
                                        Latitude = 'NULL'
                                if isnan(Longitude):
                                        Longitude = 'NULL'
                                if isnan(Altitude):
                                        Altitude = 'NULL'
                        except:
                                Latitude = 'NULL'
                                Longitude = 'NULL'
                                Altitude = 'NULL'

                        sql_query_Locations = "INSERT INTO `FloodWarningDB`.`Locations` (Location_ID, Latitude, Longitude, Altitude) VALUES('{}', {}, {}, {}) ON DUPLICATE KEY UPDATE Latitude={}, Longitude={}, Altitude={};".format(Location_ID,Latitude,Longitude,Altitude,Latitude,Longitude,Altitude)
                        cur.execute(sql_query_Locations)
                        con.commit()

                        measurements = {}

                        for database_entry in df.columns:

                                if (database_entry not in ['device_id','received_at','protocol_version']) and (database_entry.split('_')[0] != 'metadata'):

                                        variable_field = database_entry.split('_')[-1]
                                        variable_name = database_entry[:-(len(variable_field)+1)]

                                        if variable_name not in measurements:
                                                measurements[variable_name] = {variable_field: row[database_entry]}
                                        else:
                                                measurements[variable_name][variable_field] = row[database_entry]

                        for measurement in measurements:

                                Display_name = measurements[measurement]['displayName']
                                if 'unit' in measurements[measurement]:
                                        Unit = measurements[measurement]['unit']
                                        sql_query_Variables = "INSERT IGNORE INTO `FloodWarningDB`.`Variables` (Display_name, Unit) VALUES('{}', '{}');".format(Display_name, Unit)
                                        cur.execute(sql_query_Variables)
                                        con.commit()
                                else:
                                        Unit = 'NULL'
                                        sql_query_Variables = "INSERT IGNORE INTO `FloodWarningDB`.`Variables` (Display_name, Unit) VALUES('{}', {});".format(Display_name, Unit)
                                        cur.execute(sql_query_Variables)
                                        con.commit()


                                Value = measurements[measurement]['value']
                                sql_query_Values = "INSERT IGNORE INTO `FloodWarningDB`.`Measurements` (Received_at, Value, Display_name, Device_ID, Location_ID) VALUES('{}', {},'{}','{}','{}');".format(Received_at,Value,Display_name,Device_ID,Location_ID)
                                cur.execute(sql_query_Values)
                                con.commit()

        con.close()
        return None




def ingest_historical_data(ttn_application,last_days=7):

    end_day = pd.Timestamp.now()

    record_days = [(end_day-pd.Timedelta(days=day)).strftime('%Y%m%d') for day in range(last_days)]

    for record_day in record_days:

            # for ttn_application in ttn_applications:
            print(ttn_application, record_day)
            df = queryS3(ttn_application, record_day)
            ingestMySQL(df, ttn_application)

    return None


if __name__ == "__main__":

    for ttn_app in ttn_app_list:
        print("ingesting data for application "+ttn_app['application']+"...")
        ingest_historical_data(ttn_app['application'])

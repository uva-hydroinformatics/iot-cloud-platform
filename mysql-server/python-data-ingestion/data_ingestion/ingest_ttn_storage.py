import json
import urllib3
import pandas as pd
from urllib3.exceptions import HTTPError
from datetime import datetime
#from io import StringIO
import pymysql
from TTN_parameters import ttn_app_list
import MySQL_parameters
from math import isnan

#######
# TTN Data storage Integration Query

def get_headers(key):
    headers = {
        'Accept': 'text/event-stream',
        'Authorization': 'Bearer ' + key,
    }
    return headers


def get_data(ttn_application, app_key, last='1h'):
    """
    Query the data for all devices under ttn's application
    Parameters
    ----------
    time : str
        Duration on which we want to get the data (default 1h).
        Pass 30s for the last 30 seconds, 1h for the last hour,
        2d for the last 48 hours, etc
    Returns
    -------
    returns the JSON formated list data for all devices
    NOTE
    ----
    -   units return as ASCII characters, regular print(get_data(stuff)) will throw UnicodeEncodeError,
        instead use print(json.dumps(get_data(stuff)), be sure to 'import json' first
    """

    url = "https://nam1.cloud.thethings.network/api/v3/as/applications/"+ttn_application+"/packages/storage/uplink_message"
    headers = get_headers(app_key)
    fields = {'last':last}

    return get_response(url, headers , fields)

def get_response(url, headers={}, fields={}):
    """
    Parameters
    ----------
    url : str
        URL to TTN endpoint to query
    params : dict
        parameters for url
    Returns
    -------
    JSON response for url if successfull else None
    Raises
    ------
    HTTPError:
        If HTTP error occurs on TNN server side
    NOTE
    ----
    -   units return as ASCII characters, regular print(get_response(stuff)) will throw UnicodeEncodeError,
        instead use print(json.dumps(get_response(stuff)), be sure to 'import json' first
    """
    try:
        http_pool_manager = urllib3.PoolManager()
        response = http_pool_manager.request('GET', url, headers=headers, fields=fields)

        if (response.status == 200):
            return response.data.decode("utf8")
        else:
            return None

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')



#######
# Parse TTN data storage integration response


def parse_response(query_response):

    responsesJSON = json.loads("{\"data\": [" + query_response.replace("\n\n", ",")[:-1] + "]}")

    parsedJSON_list = []

    for uplink in responsesJSON["data"]:

        parsedJSON = {}
        parsedJSON["received_at"] = uplink["result"]["received_at"]

        for key in uplink["result"]["uplink_message"]["decoded_payload"]:
            if type(uplink["result"]["uplink_message"]["decoded_payload"][key]) is dict:
                for parameter in uplink["result"]["uplink_message"]["decoded_payload"][key]:
                    parsedJSON[key+'_'+parameter] = uplink["result"]["uplink_message"]["decoded_payload"][key][parameter]
            else:
                parsedJSON[key] = uplink["result"]["uplink_message"]["decoded_payload"][key]

        metadata = uplink["result"]["uplink_message"]["rx_metadata"][0]

        for key in metadata:
            if type(metadata[key]) is dict:
                for parameter in metadata[key]:
                    parsedJSON['metadata'+'_'+key+'_'+parameter] = metadata[key][parameter]
            else:
                parsedJSON['metadata'+'_'+key] = metadata[key]

        parsedJSON_list.append(parsedJSON)

    df = pd.DataFrame.from_dict(parsedJSON_list)
    df['received_at'] = pd.to_datetime(df['received_at'])
    df = df.set_index('received_at')

    return df



#######
# Ingest to MySQL database


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



if __name__ == "__main__":

    request_interval = '75m'

    for ttn_app in ttn_app_list:
        ttn_response = get_data(ttn_app['application'], ttn_app['key'], last=request_interval)

        if ttn_response:
            parsed_df = parse_response(ttn_response)
            print('ingesting data from '+ttn_app['application']+'...')
            ingestMySQL(parsed_df, ttn_app['application'])
        else:
            continue

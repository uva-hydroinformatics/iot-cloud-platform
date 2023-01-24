import paho.mqtt.client as mqtt
import time
import json
import pandas as pd
import MySQL_parameters
import pymysql
from math import isnan
from TTN_parameters import ttn_app_list


###########
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


###########
# Parse TTN response

def parse_mqtt_response(query_response):

    uplink = json.loads(query_response)

    parsedJSON = {}
    parsedJSON["received_at"] = uplink["received_at"]

    for key in uplink["uplink_message"]["decoded_payload"]:
        if type(uplink["uplink_message"]["decoded_payload"][key]) is dict:
            for parameter in uplink["uplink_message"]["decoded_payload"][key]:
                parsedJSON[key+'_'+parameter] = uplink["uplink_message"]["decoded_payload"][key][parameter]
        else:
            parsedJSON[key] = uplink["uplink_message"]["decoded_payload"][key]

    metadata = uplink["uplink_message"]["rx_metadata"][0]

    for key in metadata:
        if type(metadata[key]) is dict:
            for parameter in metadata[key]:
                parsedJSON['metadata'+'_'+key+'_'+parameter] = metadata[key][parameter]
        else:
            parsedJSON['metadata'+'_'+key] = metadata[key]


    df = pd.DataFrame.from_dict([parsedJSON])
    df['received_at'] = pd.to_datetime(df['received_at'])
    df = df.set_index('received_at')

    return df


###########
# MQTT functions

# Uncoment to print MQTT log details
def on_log(client, userdata, level, buf):
    print("<< log: "+buf+" >>")

# Uncoment to print sent message details
def on_message(client, userdata, message):
    ttn_application = message.topic.split("/")[1].split("@")[0]
    # print("\nmessage received: ", str(message.payload.decode("utf-8")))
    print("\nmessage received")
    # print("message topic = ", message.topic)
    # print("message qos = ", message.qos)
    # print("message retain flag = ", message.retain)
    print("TTN application = ", ttn_application)
    if message.topic.split("/")[-1] =="up":
        df = parse_mqtt_response(str(message.payload.decode("utf-8")))
        ingestMySQL(df, ttn_application)
        # print(df)

def on_connect(client, userdata, flags, rc):
    if rc ==0:
        print("Successfully connected")
    else:
        print("Bad connection, returned code = ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected, result code = ", str(rc))



##########
# Main Loop

if __name__ == "__main__":

    print("starting live ingestion from TTN...")

    for ttn_app in ttn_app_list:

        ###########
        # MQTT credentials and topics

        mqtt_client_id = 'MySQL_server'

        mqtt_key = ttn_app['key']
        mqtt_user = ttn_app['application']+'@ttn'

        mqtt_server = 'nam1.cloud.thethings.network'
        mqtt_port = 1883
        mqtt_topics  = [('#',0)] 

        ###########
        # Connect to MQTT Broker

        client = mqtt.Client(mqtt_client_id) # Creates a new MQTT client instance
        client.username_pw_set(username=mqtt_user,password=mqtt_key)
        client.on_message = on_message
        # client.on_log = on_log
        # client.on_connect = on_connect
        # client.on_disconnect = on_disconnect

        client.connect(mqtt_server, port=mqtt_port) # Connects to MQTT broker

        client.loop_start()

        client.subscribe(mqtt_topics)

    print("MQTT clients created...")

    while True:
        time.sleep(5)

    #time.sleep(5*60)
    #client.loop_stop()    #Stop loop
    #client.disconnect() # disconnect

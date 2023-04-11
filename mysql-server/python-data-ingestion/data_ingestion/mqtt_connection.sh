#!/bin/bash

until python3 /home/bitnami/data_ingestion/ingest_live_data.py >> /home/bitnami/data_ingestion/log_mqtt.txt 2>&1; do
    echo "'ingest_live_data.py' crashed with exit code $?. Restarting..." >> /home/bitnami/data_ingestion/log_mqtt_error.txt 2>&1
    sleep 1
done



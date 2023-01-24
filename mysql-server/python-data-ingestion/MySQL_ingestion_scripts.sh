#!/bin/bash

echo "=== starting data ingestion script ==="

python3 /home/bitnami/data_ingestion/ingest_historical_data.py

echo "historical data ingestion was completed"

bash /home/bitnami/data_ingestion/mqtt_connection.sh &

echo "started MQTT connection bash script"

sleep 300

echo "starting TTN storage integration ingestion"

python3 /home/bitnami/data_ingestion/ingest_ttn_storage.py

echo "=== startup sequence complete! ==="

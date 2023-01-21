# IoT Cloud Platform

In this project we built a IoT Cloud Platform hosted in AWS to store and visualize data from sensors connected to The Things Network (TTN). Automatic long-term data ingestion is performed periodically by an AWS Lambda function that queries sensor uplink data from the TTN data storage integration and stores it in an AWS S3 bucket. We used AWS API Gateway to build a REST API that allows users with valid authorization tokens to download sensor data. The REST API documentation is hosted as a static website using SWAGGER UI. A data server hosts a MySQL database and python scripts to download and ingest real time data from TTN through a MQTT connection and historical data from our S3 buckets. Another server hosts sensor data visualization dashboards using Grafana with the MySQL database as its data source.

# System Diagram

<img src="./images/diagram.svg">


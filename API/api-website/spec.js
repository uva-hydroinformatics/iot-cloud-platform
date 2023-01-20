var spec =

{
  "openapi": "3.0.0",
  "info": {
    "title": "Sensor Data Download API",
    "description": "This Api allows retrieval of historical sensor data from the Flood Warning System Application.  ",
    "contact": {
      "email": "vas4d@virginia.edu"
    },
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://nh7610mswb.execute-api.us-east-1.amazonaws.com/test"
    }
  ],
  "paths": {
    "/download-sensor-data": {
      "get": {
        "tags": [
          "Download"
        ],
        "summary": "Downloads historical data from LoRa sensors.",
        "description": " This GET request downloads stored sensor data filtered by the following parameters.",
        "operationId": "SensorData",
        "parameters": [
          {
            "name": "authorizationToken",
            "in": "header",
            "description": "Authorization key token.",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "application",
            "in": "query",
            "description": "TTN application to download data from.",
            "required": false,
            "explode": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "device_id",
            "in": "query",
            "description": "Device identification number of the sensor to query data from.",
            "required": false,
            "explode": true,
            "schema": {
              "type": "integer"
            }
          },
          {
            "name": "last",
            "in": "query",
            "description": "Filters most recent data within the given number of days (e.g, '4d' for the last 4 days).",
            "required": false,
            "explode": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "start_date",
            "in": "query",
            "description": "Request data starting on a specific day on the format YYYY-MM-DD (e.g, '2022-12-1' for december first of year 2022).",
            "required": false,
            "explode": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "end_date",
            "in": "query",
            "description": "Request data ending on a specific day on the format YYYY-MM-DD (e.g, '2022-12-2' for december second of year 2022).",
            "required": false,
            "explode": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Success Response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "columns": {
                      "type": "array",
                      "items": {
                        "type": "string",
                        "example": "device_id"
                      }
                    },
                    "index": {
                      "type": "array",
                      "items": {
                        "type": "number",
                        "example": 1672703803473
                      }
                    },
                    "data": {
                      "type": "array",
                      "items": {}
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
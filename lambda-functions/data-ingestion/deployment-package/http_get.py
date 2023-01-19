import json
import urllib3
from urllib3.exceptions import HTTPError

def get_headers(key):
    headers = {
        'Accept': 'text/event-stream',
        'Authorization': 'Bearer ' + key,
    }
    return headers


def get_data(ttn_application, app_key, last='1h'):

    url = "https://nam1.cloud.thethings.network/api/v3/as/applications/"+ttn_application+"/packages/storage/uplink_message"
    headers = get_headers(app_key)
    fields = {'last':last}

    return get_response(url, headers , fields)

def get_response(url, headers={}, fields={}):   

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


if __name__ == "__main__":
    print("This module contains functions to query TTN sensor data from a given application.") 
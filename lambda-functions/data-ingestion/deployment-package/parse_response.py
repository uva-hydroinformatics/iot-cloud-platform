import json
import pandas as pd

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

         
if __name__ == "__main__":
    print("This module contains functions to parse a query response from TTN.") 
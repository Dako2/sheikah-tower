import requests
import math
import logging
import json
import time

logging.basicConfig(level=logging.INFO, filename='api_responses.log', format='%(asctime)s - %(message)s')

# todo to add concurrent.futures to make multiple requests concurrently
def fetch_user_coordinates(api_url="http://127.0.0.1:9091/get_location"):
    try:
        response = requests.get(api_url)
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            return data['latitude'], data['longitude'], data['timestamp_seconds']
        else:
            #print(f"Error: Received status code {response.status_code}")
            return {}
    except requests.RequestException as e:
        #print(f"Error fetching location data: {e}")
        return {}
    
def fetch_user_coordinates_zoneid_cellid_virtual(api_url="http://127.0.0.1:9091/get_location"):
    try:
        response = requests.get(api_url)
        
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            return data['latitude'], data['longitude'], data['timestamp_seconds'], data['cellid'], data['zoneid']
        else:
            #print(f"Error: Received status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching location data: {e}")
        return None
    
def fetch_userlist_in_zone(zone_id):
    api_url = f'https://try-mec.etsi.org/sbxvfgnt57/mep2/location/v2/queries/users?zoneId={zone_id}'
    response = requests.get(api_url)

    if response.status_code == 200: # successful
        data = response.json()['userList']['resourceURL'] # {'userList': {'resourceURL': 'https://try-mec.etsi.org/sbxvfgnt57/mep2/location/v2/queries/users'}}
        """{'userList': {'resourceURL': 'https://try-mec.etsi.org/sbxvfgnt57/mep2/location/v2/queries/users', 'user':  [{'accessPointId': '5g-small-cell-13', 'address': '10.100.0.4', 'locationInfo': {'latitude': [43.74588], 'longitude': [7.432222], 'shape': 2, 'timestamp': {'nanoSeconds': 0, 'seconds': 1693526572}}, 'resourceURL': 'https://try-mec.etsi.org/sbxvfgnt57/mep2/location/v2/queries/users?address=10.100.0.4', 'timestamp': {'nanoSeconds': 0, 'seconds': 1693526572}, 'zoneId': 'zone04'}, 
                                                                                                                    {'accessPointId': '4g-macro-cell-9', 'address': '10.100.0.1', 'locationInfo': {'latitude': [43.748833], 'longitude': [7.434197], 'shape': 2, 'timestamp': {'nanoSeconds': 0, 'seconds': 1693526572}}, 'resourceURL': 'https://try-mec.etsi.org/sbxvfgnt57/mep2/location/v2/queries/users?address=10.100.0.1', 'timestamp': {'nanoSeconds': 0, 'seconds': 1693526572}, 'zoneId': 'zone04'}, 
                                                                                                   {'accessPointId': 'wifi-ap-10', 'address': '10.1.0.4', 'locationInfo': {'latitude': [43.74835], 'longitude': [7.438248], 'shape': 2, 'timestamp': {'nanoSeconds': 0, 'seconds': 1693526572}}, 'resourceURL': 'https://try-mec.etsi.org/sbxvfgnt57/mep2/location/v2/queries/users?address=10.1.0.4', 'timestamp': {'nanoSeconds': 0, 'seconds': 1693526572}, 'zoneId': 'zone04'}]}}
        """
        userlist = requests.get(data).json()
        return userlist
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None

def fetch_distance(address1, latitude, longitude):
    api_url = f'https://try-mec.etsi.org/sbxvfgnt57/mep2/location/v2/queries/distance?address={address1}&latitude={latitude}&longitude={longitude}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json() # {'terminalDistance': {'distance': 341, 'timestamp': {'nanoSeconds': 0, 'seconds': 1693533286}}}
        distance = data['terminalDistance']['distance']
        return distance # int
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None

def fetch_user_coordinates_real(ip_address, fetchURL='https://try-mec.etsi.org/sbxkbwuvda/mep2/location/v2/queries/users?address='):
    api_url = f'{fetchURL}{ip_address}'
    response = requests.get(api_url)
    
    if response.status_code == 200: # successful
        response = response.json()
        latitude = response['userList']['user'][0]['locationInfo']['latitude'][0] # [0] first element of the list
        longitude = response['userList']['user'][0]['locationInfo']['longitude'][0]
        timestamp_seconds = response['userList']['user'][0]['locationInfo']['timestamp']['seconds']
        return latitude, longitude, timestamp_seconds
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None, None, None

def fetch_user_coordinates_zoneid_cellid(ip_address ="10.10.0.4", fetchURL='https://try-mec.etsi.org/sbxkbwuvda/mep1/location/v2/queries/users?address='):
    api_url = f'{fetchURL}{ip_address}'
    response = requests.get(api_url)
    
    if response.status_code == 200: # successful
        response = response.json()
        print(response)
        cellid = response['userList']['user'][0]['accessPointId'] # [0] first element of the list
        zoneid = response['userList']['user'][0]['zoneId']
        latitude = response['userList']['user'][0]['locationInfo']['latitude'][0] # [0] first element of the list
        longitude = response['userList']['user'][0]['locationInfo']['longitude'][0]
        timestamp_seconds = response['userList']['user'][0]['locationInfo']['timestamp']['seconds']

        # Log the data
        logging.info(json.dumps(response))
        # Save to a file (you can adjust this if you want to save in a different format or location)
        with open('api_responses.json', 'a') as file:
            json.dump(response, file)
            file.write('\n')  # Separate each JSON object with a newline

        return latitude, longitude, timestamp_seconds, cellid, zoneid
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None, None, None, None, None
#print(fetch_user_coordinates('10.100.0.4'))

def distance_calc(lat1, lon1, lat2, lon2):
    # Radius of the Earth in meters
    R = 6371000  # Earth's radius in meters

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula - distance between two coordinates
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

# print(distance_calc(43.730785, 7.420383, 43.739648, 7.427329)) # output: 1132.556840778062
if __name__ == '__main__':
    ip_address = '10.100.0.3'  # Replace with your IP address

    while True:
        print(fetch_user_coordinates_zoneid_cellid(ip_address))
        time.sleep(1)

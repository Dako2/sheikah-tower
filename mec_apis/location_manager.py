"""
location API manager
Main Zone for demo:zone02 (many options for historical tourism spots, food, mesuems) 
Demo for communication across zones (hospital in zone01)

Step 1: once user initiate the conversation, retrieve live location. Refresh every [1] min (or area enter subscription), saved in json file as log events data
Step 2: retrieve the surrounding locations within [5] meters of user coordinates, saved in [?] a list nearby_locations_list
Step 3: based on the goal of the conversation / chat history, gather {data} from these locations, saved in [?].
Step 4: use the {data} to generate LLM response / translation
Step 5: fine-tuning model locally every 24 hours
"""

import requests
import time
import math
import json
from mec_apis.mec_location_api import fetch_user_coordinates, distance_calc

class LocationManager:
    def __init__(self, user_IP_address, log_file_path, db_location_file_path):
        self.db_location_file_path = db_location_file_path
        self.locations = self._read_locations(self.db_location_file_path)
        self.radius = 100
        self.user_IP_address = user_IP_address
        self.log_file_path = log_file_path

    # read the locations and their coordinates from the db
    def _read_locations(self, db_location_file_path):
        with open(self.db_location_file_path, 'r') as location_json_file:
            locations = json.load(location_json_file)
        return locations

    def fetch_nearby_locations(self):
        user_live_coor = fetch_user_coordinates(self.user_IP_address)
        nearby_locations_list = []

        for location, coordinates in self.locations.items(): # key, values
            distance = distance_calc(user_live_coor[0], user_live_coor[1], coordinates["latitude"], coordinates["longitude"])
            """ A sample result
            (43.746475, 7.433062, 1693767018)
            2020.2393897489778
            2348.1049487726063
            887.9064613208305
            2212.381710312174
            1858.43488196901
            1709.455407904061
            1344.2731778778702
            474.79232706685116
            """
            if distance < self.radius:
                nearby_locations_list.append(location)
                # prompt_nearby_locations = f"Now user is close to: {', '.join(nearby_locations_list)}"
        
        event = {
            "user_live_coor": {
                "latitude": float(user_live_coor[0]),
                "longitude": float(user_live_coor[1])
            },
            "time": user_live_coor[2], 
            f"nearby_locations within {self.radius}": nearby_locations_list
        }

        # write above event info into user_event_log file
        with open(self.log_file_path, 'a') as json_file:
            json.dump(event, json_file)
            json_file.write('\n')

        return event
        # time.sleep(2) # in second; todo think about the refresh frequency. Now refresh the nearby location by response
        # todo interestRealm. Thinking about the data saved under the zone - access point. Maybe shorten the list into one zone so that the calculation is easier
        """ Sample event:
        {'user_live_coor': {'latitude': 43.74216, 'longitude': 7.430558}, 
        'time': 1693770672, 
        'nearby_locations within 500': ['Monte Carlo Casino', 'Japanese Garden in Monaco']}
        """

# user_IP_address = '10.100.0.4'

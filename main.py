import openai
from environment import OPENAI_API_KEY
from datetime import datetime
openai.api_key = OPENAI_API_KEY
#from search.search_client import search_db
from llm.llm_agent import Conversation
#from ebd.ebd import text_to_ebds_csv
from mec_apis.location_manager import LocationManager
from VecDB import VecDataBase
import wrapper
# [skip if saved already] convert text in db into embeddings
#text_to_ebds_csv('db/exhibit-info.csv','db/exhibit-info-ebds.csv')
#text_to_ebds_csv('db/user-data.csv','db/user-data-ebds.csv')
# initiate a conversation
convo = Conversation()

"""
# initatie a location manager
log_file_path = "db/user_event_log_file.json"
db_location_file_path = "db/monaco_coordinates.json"
user_IP_address = '10.100.0.4'
locationManager = LocationManager(user_IP_address, log_file_path, db_location_file_path)
event = locationManager.fetch_nearby_locations()

# @Qi live information to present by UI
user_live_coor = f"User now at: {event['user_live_coor']}"
nearby_locations = f"{list(event.keys())[2]}: {event[list(event.keys())[2]]}" # 3rd key is 'nearby_locations within 500'

# check to delete
print(user_live_coor)
print(nearby_locations)
"""

# initiate VecDataBase class
DATA_PATH={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
v = VecDataBase(db_csv_paths = DATA_PATH, update_db=True)
MODE_CHOICE = "1" 

# initiate location information
mec = wrapper.MECApp()

try:
    while True:
        user_input = input("\n\nUser: ")
        if MODE_CHOICE == '0':
            found_user_db = mec.desert_mode(user_input)
            found_loc_db = None
            user_location_info = mec.loc_api()[1] # = none, if nothing is within nearby area of [500] meters
        elif MODE_CHOICE == '1':
            search_results = mec.spot_mode(user_input)
            found_user_db = search_results[2]
            found_loc_db = search_results[0]
            user_location_info = None # e.g. currently within the museum. Maybe add detailed location information (within museum) in the future
        else: 
            print("...Invalid choice.")
        output = convo.rolling_convo(user_input, found_loc_db, found_user_db, user_location_info)
except KeyboardInterrupt:
    print("...Keyboard Interrupted!")


"""
# todo modules to build
1. mechanism/agent to ask users' confirmation: some research on langchain agent
2. mark the location_database with coordinates. When it's [5] meters close, ask about if you are interested going in -> switch to the database
3. two prompts (one desert mode; mode museum mode)
"""

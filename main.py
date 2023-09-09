import openai
from environment import OPENAI_API_KEY
from datetime import datetime
openai.api_key = OPENAI_API_KEY
#from search.search_client import search_db
from llm.llm_agent import Conversation
#from ebd.ebd import text_to_ebds_csv
from mec_apis.location_manager import LocationManager
from VecDB import VecDataBase
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

DATA_PATH={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
v = VecDataBase(db_csv_paths = DATA_PATH, update_db=True)

try:
    while True:
        user_input = input("\n\nUser: ")
        loc1_found_db_texts, loc1_found_score = v.search_db(user_input, DATA_PATH['loc1'])
        print(loc1_found_db_texts)
        user_found_db_texts, user_found_score = v.search_db(user_input, DATA_PATH['user1'])
        print(user_found_db_texts)      
        
        output = convo.rolling_convo(user_input, loc1_found_db_texts, user_found_db_texts)
        print(output)
except KeyboardInterrupt:
    print("Keyboard Interrupted!")

# todo modules to build
"""
1. mechanism/agent to ask users' confirmation: some research on langchain agent
2. mark the location_database with coordinates. When it's [5] meters close, ask about if you are interested going in -> switch to the database
3. two prompts (one desert mode; mode museum mode)
"""

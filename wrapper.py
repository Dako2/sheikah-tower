import openai
from environment import OPENAI_API_KEY
from datetime import datetime
openai.api_key = OPENAI_API_KEY
from llm.llm_agent import Conversation
from mec_apis.location_manager import LocationManager
from VecDB import VecDataBase
from mec_apis.mec_location_api import fetch_user_coordinates

# [skip if saved already] convert text in db into embeddings
#text_to_ebds_csv('db/loc_apiexhibit-info.csv','db/exhibit-info-ebds.csv')
#text_to_ebds_csv('db/user-data.csv','db/user-data-ebds.csv')
DATA_PATH={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
FETCH_URL = 'https://try-mec.etsi.org/sbxkbwuvda/mep2/location/v2/queries/users?address='

class MECApp():
    def __init__(self) -> None:
        self.convo = Conversation()
        log_file_path = "db/user_event_log_file.json"
        db_location_file_path = "db/monaco_coordinates.json"
        user_IP_address = '10.100.0.4'
        self.locationManager = LocationManager(user_IP_address, log_file_path, db_location_file_path, FETCH_URL)
        self.v = VecDataBase(db_csv_paths = DATA_PATH, update_db=True)
        self.nearby_locations = ""
        
    def chat_api(self, user_input):
        loc1_found_db_texts, loc1_found_score = self.v.search_db(user_input, DATA_PATH['loc1'])
        user_found_db_texts, user_found_score = self.v.search_db(user_input, DATA_PATH['user1'])
        output = self.convo.rolling_convo(user_input, loc1_found_db_texts, user_found_db_texts, self.nearby_locations)
        print(self.convo.messages)
        return output
    
    def loc_api(self, radius = 1000):
        nearby_locations = None
        event = self.locationManager.fetch_nearby_locations(radius)
        user_live_coor = f"User now at: {event['user_live_coor']}"
        if event[list(event.keys())[2]]:
            self.nearby_locations = f"{list(event.keys())[2]}: {event[list(event.keys())[2]]}" # nearby_locations within 500: ['Monte Carlo Casino', 'Japanese Garden in Monaco']
        return user_live_coor, self.nearby_locations, event
    
    def loc_user_api(self, ip_addr = '10.100.0.1'):
        user_live_coor = fetch_user_coordinates(ip_addr)
        return user_live_coor
    
    def desert_mode(self, user_input): # use user db, city coordinates & user location (outside this function)
        #loc1_found_db_texts, loc1_found_score = self.v.search_db(user_input, DATA_PATH['loc1'])
        user_found_db_texts, user_found_score = self.v.search_db(user_input, DATA_PATH['user1'])
        return user_found_db_texts, user_found_score # output tuple ('', [], '', [])

    def spot_mode(self, user_input): # use user db, spot db (e.g. museum), no user location (already entered the place)
        loc1_found_db_texts, loc1_found_score = self.v.search_db(user_input, DATA_PATH['loc1'])
        user_found_db_texts, user_found_score = self.v.search_db(user_input, DATA_PATH['user1'])
        return loc1_found_db_texts, loc1_found_score, user_found_db_texts, user_found_score # output tuple ('', [], '', [])

    def if_enter_a_spot(self):
        confirmation = True
        positive_confirmations = ["yes", "ok", "sure", "of course", "let's do it", "fine", "yeah", "yup"]
        #if self.
        # ()[1]:
            #nearby_locations = self.loc_api()[1]
            #user_input = input(f"Are you interested in exploring these nearby spots further with me? {nearby_locations}").lower()
            #if any(word in user_input for word in positive_confirmations):
            #    confirmation = True
        return confirmation
    
    def if_leave_a_spot(self):
        return False # TODO   

if __name__ == "__main__":
    mec = MECApp()
    print(mec.loc_api(radius = 1000))

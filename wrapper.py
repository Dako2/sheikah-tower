import openai
from environment import OPENAI_API_KEY
from datetime import datetime
openai.api_key = OPENAI_API_KEY
from llm.llm_agent import Conversation
from mec_apis.location_manager import LocationManager
from VecDB import VecDataBase

# [skip if saved already] convert text in db into embeddings
#text_to_ebds_csv('db/exhibit-info.csv','db/exhibit-info-ebds.csv')
#text_to_ebds_csv('db/user-data.csv','db/user-data-ebds.csv')
DATA_PATH={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}

class MECApp():
    def __init__(self) -> None:
        self.convo = Conversation()
        log_file_path = "db/user_event_log_file.json"
        db_location_file_path = "db/monaco_coordinates.json"
        user_IP_address = '10.100.0.4'
        self.locationManager = LocationManager(user_IP_address, log_file_path, db_location_file_path)

        self.v = VecDataBase(db_csv_paths = DATA_PATH, update_db=True)
        
    def chat_api(self, user_input):
        loc1_found_db_texts, loc1_found_score = self.v.search_db(user_input, DATA_PATH['loc1'])
        #print(loc1_found_db_texts)
        user_found_db_texts, user_found_score = self.v.search_db(user_input, DATA_PATH['user1'])
        #print(user_found_db_texts)
        output = self.convo.rolling_convo(user_input, loc1_found_db_texts, user_found_db_texts)
        print(self.convo.messages)
        return output
    
    def loc_api(self):
        # @Qi live information to present by UI
        event = self.locationManager.fetch_nearby_locations()
        user_live_coor = f"User now at: {event['user_live_coor']}"
        nearby_locations = f"{list(event.keys())[2]}: {event[list(event.keys())[2]]}" # 3rd key is 'nearby_locations within 500'

        return user_live_coor, nearby_locations

if __name__ == "__main__":
    mec = MECApp()

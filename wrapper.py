import openai
from environment import OPENAI_API_KEY
from datetime import datetime
openai.api_key = OPENAI_API_KEY
from llm.llm_agent import Conversation
#from mec_apis.location_manager import LocationManager
from VecDB import VecDataBase
from mec_apis.mec_location_api import fetch_user_coordinates, fetch_user_coordinates_zoneid_cellid, fetch_user_coordinates_zoneid_cellid_real
import json
import time
import image_vecdb
# [skip if saved already] convert text in db into embeddings
#text_to_ebds_csv('db/loc_apiexhibit-info.csv','db/exhibit-info-ebds.csv')
#text_to_ebds_csv('db/user-data.csv','db/user-data-ebds.csv')
DATA_PATH={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
FETCH_URL = 'https://try-mec.etsi.org/sbxkbwuvda/mep1/location/v2/queries/users?address='

def load_jsonl(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]
    
class MECApp():
    def __init__(self, user_IP_address = '10.100.0.1') -> None:
        self.convo = Conversation()
        #log_file_path = "db/user_event_log_file.json"
        #db_location_file_path = "db/monaco_coordinates.json"
        self.ip_addr = user_IP_address
        #self.locationManager = LocationManager(user_IP_address, log_file_path, db_location_file_path, FETCH_URL)
        self.v = VecDataBase(db_csv_paths = DATA_PATH, update_db=True)
        self.places_dict = {}
        with open('monoco_zone_cellid_places.json', 'r') as file:
            self.db_json = json.load(file) 
        self.cellid = None
        self.zoneid = None
        self.image_db = image_vecdb.ImageVecDataBase('./db/images', './db/images/embeddings')
        self.image_db_jsonlist = load_jsonl("./db/images/metadata.jsonl")
        
    def analyze_image_api(self, filename = './upload/image.jpeg'):
        # Read image
        img = image_vecdb.Image.open(filename)
        most_similar_img, most_similar_img_idx, sim_score = self.image_db.search_db(img)
        
        print("Score: %.4f" % (sim_score))
        print("Index of most similar image in DB: %d" % (most_similar_img_idx))
        print(self.image_db_jsonlist[most_similar_img_idx])
        #return sim_score, most_similar_img_idx
        return [sim_score, self.image_db_jsonlist[most_similar_img_idx]]

    def loc_user_places_api(self):
        
        latitude, longitude, _, self.cellid, self.zoneid = fetch_user_coordinates_zoneid_cellid_real()
        # todo to delete below
        self.cellid, self.zoneid = "4g-macro-cell-4", "zone02"
        print("\n\n****************",latitude, longitude, _, self.cellid, self.zoneid)
        try:
            self.places_dict = self.db_json[self.zoneid][self.cellid]["places"]
            place_names = ', '.join(map(str, self.places_dict.keys()))
            self.convo.messages[0]["content"] = self.convo.messages[0]["content"].replace("[locations]", place_names)
            print(f"\n\n{self.convo.messages}\n\n")
            return (latitude, longitude), self.places_dict #(latitude, longitude) Egyption Museum: 43.731724, 7.423574
        except:
            return (None, None), {}
        
    def chat_api(self, user_input):
        print("Yi asked if this is running?????")
        loc1_found_db_texts = ""
        self.loc_user_places_api()
        #time.sleep(1)
       
        if self.places_dict:
            for loc_name, value in self.places_dict.items(): #loc_name, loc_dictionary: lat, long, db_path
                try:
                    print(f"searching{loc_name}:{value}")
                    text, loc1_found_score = self.v.search_db(user_input, value['db_path'])
                    loc1_found_db_texts += text
                    print(f"Found loc info {loc_name}: {text}")
                except:
                    print("bypassing..........\n\n\n")

        print("Yi asked if this is running three?????")
        user_found_db_texts, user_found_score = self.v.search_db(user_input, DATA_PATH['user1'])

        output = self.convo.rolling_convo(user_input, loc1_found_db_texts, user_found_db_texts)
        print("\n\n\n===============", self.convo.messages, "==============================\n\n\n")

        return output
    
    """
    def loc_api(self, radius = 1000):
        nearby_locations = None
        event = self.locationManager.fetch_nearby_locations(radius)
        user_live_coor = f"User now at: {event['user_live_coor']}"

        if event[list(event.keys())[2]]:
            self.nearby_locations = f"{list(event.keys())[2]}: {event[list(event.keys())[2]]}" # nearby_locations within 500: ['Monte Carlo Casino', 'Japanese Garden in Monaco']
        return user_live_coor, self.nearby_locations, event
    """
    
    def loc_user_api(self,):
        try:
            user_live_coor = fetch_user_coordinates(self.ip_addr, FETCH_URL)
            return user_live_coor
        except:
            print("user loc cannot be found")
            return (None, None)
    
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
    mec = MECApp('10.100.0.1')
    
    mec.loc_user_places_api()
    print('\n\n\n\n')
    #mec.chat_api("hello, any interesting spots? ")
    #mec.analyze_image_api('./test_data/images/test_0001.jpeg')

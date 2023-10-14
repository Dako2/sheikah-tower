import json
from datetime import datetime

import openai
import image_vecdb
from llm.llm_agent import Conversation
from VecDB import VecDataBase
from mec_apis.mec_location_api import (fetch_user_coordinates, 
                                       fetch_user_coordinates_zoneid_cellid, 
                                       fetch_user_coordinates_zoneid_cellid_real)
from mec_apis.mec_virutal_server import VirtualMEC
from environment import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

DATA_PATH = {
    'loc1': './db/ocp/ocp.json',
    'loc2': './db/ocp/ocp_speakers.json',
    'user1': './db/users/user-data.json'
}

FETCH_URL = "https://try-mec.etsi.org/sbxkbwuvda/mep1/location/v2/queries/users?address="
DEFAULT_PROMPT = "Respond friendly, cheerfully and concisely within 50 words. Keep the conversation's flow by politely asking short question or for clarification or additional details when unsure."
DEFAULT_PROMPT_PHOTO = "The user took a photo." #the user input prompt in image case
UPDATE_VectDataBase = False


def load_jsonl(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

class MECApp:
    def __init__(self, user_IP_address='10.100.0.1') -> None:
        self.convo = Conversation()
        self.ip_addr = user_IP_address

        self.v = VecDataBase(DATA_PATH, update_db=UPDATE_VectDataBase)
        self.mec_virtual = VirtualMEC()
        self.places_dict = {}
        
        with open("./db/monoco_zone_cellid_places.json", 'r') as file:
            self.db_json = json.load(file)
        
        self.cellid = None
        self.zoneid = None
        self.image_db = image_vecdb.ImageVecDataBase('./db/images', './db/images/embeddings')

    def analyze_image_api(self, filename='./upload/image.jpeg'):
        img = image_vecdb.Image.open(filename)
        
        try:
            most_similar_img, most_similar_img_idx, sim_score = self.image_db.search_db(img)
            
            output = self.convo.rolling_convo(DEFAULT_PROMPT_PHOTO, self.image_db.db_image_prompt(most_similar_img_idx), "")
            
            return [sim_score, self.image_db.db_image_info(most_similar_img_idx), output]
        except:
            return [None, None, None]
        
    def loc_user_places_api(self):
        latitude, longitude, _, self.cellid, self.zoneid = self.mec_virtual.fetch_user_coordinates_zoneid_cellid()
        try:
            self.places_dict = self.db_json[self.zoneid][self.cellid]["places"]
            place_names = ', '.join(map(str, self.places_dict.keys()))
            self.convo.messages[0]["content"] = f"Be an assistant and guide at {place_names}. " + DEFAULT_PROMPT
            return (latitude, longitude), self.places_dict
        except:
            return (None, None), {}

    def chat_api(self, user_input):
        loc1_found_db_texts = ""
        score = []
        if self.places_dict:
            for loc_name, places in self.places_dict.items():
                try:
                    print("\nxxx\n", loc_name, "\nxxx\n", places['db_path'],"\nxxx\n")
                    text, score = self.v.search_db(user_input, places['db_path'], threshold=0.6, top_n = 3)
                    loc1_found_db_texts += text
                except:
                    pass
        #loc1_found_db_texts = loc1_found_db_texts[:1000] #todo adjust length of pulled db text
        #user_found_db_texts, _ = self.v.search_db(user_input, DATA_PATH['user1'])
        user_found_db_texts = ""

        print(f"{loc1_found_db_texts}\n\n======found vector above database=======\n")
        print(f"Score: {score}") # todo to delete when clean up

        output = self.convo.rolling_convo(user_input, loc1_found_db_texts, user_found_db_texts)
        
        return output
    
    def loc_user_api(self):
        try:
            return fetch_user_coordinates()
        except:
            print("user loc cannot be found")
            return (None, None)

    def desert_mode(self, user_input):
        user_found_db_texts, user_found_score = self.v.search_db(user_input, DATA_PATH['user1'])
        return user_found_db_texts, user_found_score

    def spot_mode(self, user_input):
        loc1_found_db_texts, loc1_found_score = self.v.search_db(user_input, DATA_PATH['loc1'])
        user_found_db_texts, user_found_score = self.v.search_db(user_input, DATA_PATH['user1'])
        return loc1_found_db_texts, loc1_found_score, user_found_db_texts, user_found_score

    def if_enter_a_spot(self):
        return True  # TODO: Implement further logic

    def if_leave_a_spot(self):
        return False  # TODO: Implement further logic


if __name__ == "__main__":
    mec = MECApp('10.100.0.1')
    mec.loc_user_places_api()
    
    try:
        while True:  # keep running until Ctrl+C is pressed
            user_input = input("Please enter something: ")
            mec.chat_api(user_input)
            
    except KeyboardInterrupt:
        print("\nExiting the program.")
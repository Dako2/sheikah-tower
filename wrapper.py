import json
from datetime import datetime

import openai
import image_vecdb_v2
from llm.llm_agent import Conversation
from VecDB import VecDataBase
from mec_apis.mec_location_api import (fetch_user_coordinates, 
                                       fetch_user_coordinates_zoneid_cellid, 
                                       fetch_user_coordinates_zoneid_cellid_real)
from environment import OPENAI_API_KEY
from PIL import Image

openai.api_key = OPENAI_API_KEY

DATA_PATH = {
    #'loc1': './db/ocp/ocp.json',
    #'loc2': './db/ocp/ocp_speakers.json',
    #'user': './db/users/user-data.json'
}

FETCH_URL = "https://try-mec.etsi.org/sbxkbwuvda/mep1/location/v2/queries/users?address="
DEFAULT_PROMPT = "Respond friendly, cheerfully and concisely within 50 words. Keep the conversation's flow by politely asking short question or for clarification or additional details when unsure."
DEFAULT_PROMPT_PHOTO = """
The user just took a photo. 
Tell the user a story about the photo, it can be history related, a fun fact, 
future event or just any stories that can raise the user's interests.
At the end of the conversation, ask the user a related question that the user might be able to guess.
"""
#the user input prompt in image case
UPDATE_VectDataBase = True

def load_jsonl(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

class SheikahApp:
    def __init__(self, db_paths, image_db_paths, update_db) -> None:
        self.convo = Conversation()
        self.v = VecDataBase(db_paths, update_db)
        self.places_dict = {}
        self.image_db = image_vecdb_v2.ImageVecDataBaseV2(image_db_paths[0],image_db_paths[1])

    def analyze_image_api(self, filename='./upload/image.jpeg'):
        img = Image.open(filename)
        try:
            most_similar_img, most_similar_img_idx, sim_score = self.image_db.search_db(img)

            print(f"image score: {sim_score}")
            
            output = self.convo.rolling_convo("", self.image_db.db_image_prompt(most_similar_img_idx), DEFAULT_PROMPT_PHOTO)
            
            return [sim_score, self.image_db.db_image_info(most_similar_img_idx), output]
        except:
            return [None, None, None]

    def chat_api(self, user_input):
        loc1_found_db_texts = ""
        score = []
        if self.places_dict:
            for loc_name, places in self.places_dict.items():
                print("\nxxx\n", loc_name, "\nxxx\n", places['db_path'],"\nxxx\n")
                text, score = self.v.search_db(user_input, places['db_path'], threshold=0.5, top_n = 5)
                print(text, score)
                loc1_found_db_texts += text
                
        #loc1_found_db_texts = loc1_found_db_texts[:1000] #todo adjust length of pulled db text
        #user_found_db_texts, _ = self.v.search_db(user_input, DATA_PATH['user1'])
        user_found_db_texts = ""

        print(f"{loc1_found_db_texts}\n\n======found vector above database=======\n")
        print(f"Score: {score}") # todo to delete when clean up

        output = self.convo.rolling_convo(user_input, loc1_found_db_texts, user_found_db_texts)
        
        return output

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
    mec = SheikahApp('10.100.0.1')
    mec.loc_user_places_api()
    
    try:
        while True:  # keep running until Ctrl+C is pressed
            user_input = input("Please enter something: ")
            mec.chat_api(user_input)
            
    except KeyboardInterrupt:
        print("\nExiting the program.")
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
    'loc1': 'db/exhibit-info.csv',
    'user1': 'db/user-data.csv'
}

FETCH_URL = 'https://try-mec.etsi.org/sbxkbwuvda/mep1/location/v2/queries/users?address='


def load_jsonl(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]


class MECApp:
    def __init__(self, user_IP_address='10.100.0.1') -> None:
        self.convo = Conversation()
        self.ip_addr = user_IP_address
        self.v = VecDataBase(db_csv_paths=DATA_PATH, update_db=True)
        self.mec_virtual = VirtualMEC()
        self.places_dict = {}
        with open('./db/monoco_zone_cellid_places.json', 'r') as file:
            self.db_json = json.load(file)
        self.cellid = None
        self.zoneid = None
        self.image_db = image_vecdb.ImageVecDataBase('./db/images', './db/images/embeddings')

    def analyze_image_api(self, filename='./upload/image.jpeg'):
        img = image_vecdb.Image.open(filename)
        try:
            most_similar_img, most_similar_img_idx, sim_score = self.image_db.search_db(img)
            self.convo.messages = [{
                "role": "system",
                "content": self.image_db.db_image_prompt(most_similar_img_idx)
            }]
            return [sim_score, self.image_db.db_image_info(most_similar_img_idx), self.image_db.db_image_prompt(most_similar_img_idx)]
        except:
            return [None, None, None]

    def loc_user_places_api(self):
        latitude, longitude, _, self.cellid, self.zoneid = self.mec_virtual.fetch_user_coordinates_zoneid_cellid()
        try:
            self.places_dict = self.db_json[self.zoneid][self.cellid]["places"]
            place_names = ', '.join(map(str, self.places_dict.keys()))
            self.convo.messages[0]["content"] = f"be a helpful local guide at {place_names}. Respond concisely and cheerfully."
            return (latitude, longitude), self.places_dict
        except:
            return (None, None), {}

    def chat_api(self, user_input):
        loc1_found_db_texts = ""
        if self.places_dict:
            for loc_name, value in self.places_dict.items():
                try:
                    text, _ = self.v.search_db(user_input, value['db_path'])
                    loc1_found_db_texts += text
                except:
                    pass
        user_found_db_texts, _ = self.v.search_db(user_input, DATA_PATH['user1'])
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

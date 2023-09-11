import openai
from environment import OPENAI_API_KEY
from datetime import datetime
openai.api_key = OPENAI_API_KEY
from llm.llm_agent import Conversation
from mec_apis.location_manager import LocationManager
from VecDB import VecDataBase
import wrapper
# [skip if saved already] convert text in db into embeddings
#text_to_ebds_csv('db/exhibit-info.csv','db/exhibit-info-ebds.csv')
#text_to_ebds_csv('db/user-data.csv','db/user-data-ebds.csv')
# initiate a conversation
convo = Conversation()

# initiate VecDataBase class
DATA_PATH={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
v = VecDataBase(db_csv_paths = DATA_PATH, update_db=True)

# initiate location information
mec = wrapper.MECApp()
MODE_CHOICE = 0 # desert_mode default = 0

try:
    while True:
        user_input = input("\nUser: ")
        if MODE_CHOICE == 0 and mec.if_enter_a_spot(): # enter a specific spot
            MODE_CHOICE = 1
            convo.messages[0]["content"] = convo.PROMPT_LIST[1]["spot_mode"]
        elif MODE_CHOICE == 1 and mec.if_leave_a_spot(): # TODO need to add when to leave the spot and back to desert mode
            MODE_CHOICE = 0

        if MODE_CHOICE == 0:
            found_user_db = mec.desert_mode(user_input)
            found_loc_db = None
            user_location_info = mec.loc_api()[1] # = none, if nothing is within nearby area of [500] meters
        elif MODE_CHOICE == 1:
            search_results = mec.spot_mode(user_input)
            found_user_db = search_results[2]
            found_loc_db = search_results[0]
            user_location_info = None # e.g. currently within the museum. Maybe add detailed location information (within museum) in the future
        else: 
            print("...Invalid choice.")

        output = convo.rolling_convo(user_input, found_loc_db, found_user_db, user_location_info)
except KeyboardInterrupt:
    print("...Keyboard Interrupted!")
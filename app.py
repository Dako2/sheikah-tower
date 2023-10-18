from flask import Flask, request, jsonify
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging
from llm.llm_agent import Conversation
import openai
from environment import OPENAI_API_KEY
import wrapper
import os
from mec_apis.mec_virutal_server import VirtualMEP
import mec_apis.mec_location_api as MEP

from uuid import uuid4
import json

mep = VirtualMEP()
#mep = MEP
ip_address = "10.10.0.4"

# Initialize executor and set workers
executor = ThreadPoolExecutor(max_workers=4)

openai.api_key = OPENAI_API_KEY
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set up Flask and logging
app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATA_PATHS = ['./db/ocp/ocp.json', './db/sanjose/Egyptian_Museum.json']
with open("./db/zone_cellid_places.json", 'r') as file:
    db_json = json.load(file)

mec = wrapper.SheikahApp(db_paths = DATA_PATHS, image_db_paths = ('./db/images', './db/images/embeddings'), update_db = False)

def fetch_places_data():
    latitude, longitude, _, cellid, zoneid = mep.fetch_user_coordinates_zoneid_cellid()
    try:
        places_dict = db_json[zoneid][cellid]["places"]
        """
        'places': {
            'ocp-summit-2023': {'latitude': 37.3289935, 'longitude': -121.8890406, 'db_path': './db/ocp/ocp.json'}, 
            'ocp-speakers': {'latitude': 37.3285192, 'longitude': -121.8896465, 'db_path': './db/ocp/ocp_speakers.json'}, 
            'user': {'latitude': 37.3291639, 'longitude': -121.889011, 'db_path': ''}
            }
        """
        #convo.messages[0]["content"] = f"Be an assistant and guide at {place_names}." + DEFAULT_PROMPT
        place_names = ', '.join(map(str, places_dict.keys()))
        return (latitude, longitude), places_dict
    except:
        return (None, None), {}

@app.route('/api/places', methods=['POST'])
def places_api():
    (lat, lgn), nearby_locations = executor.submit(fetch_places_data).result()
    #nearby_locations['user'] = {'latitude': lat, 'longitude': lgn,'db_path':''}
    logging.info(f'Nearby locations: {nearby_locations}')
    #print({"message":{'latitude': lat, 'longitude': lgn, 'places': nearby_locations}})
    nearby_locations['user'] = {'latitude': lat, 'longitude': lgn, 'db_path': ''}
    return jsonify({"message":{'latitude': lat, 'longitude': lgn, 'places': nearby_locations}})

@app.route('/api/place_tapped', methods=['POST'])
def place_tapped():
    data = request.get_json()  # Get JSON payload
    try:
        user_id = data.get('user_id')  # Get the user ID
    except:
        print("no user id found")
        user_id = "anonymous"
    place_name = data.get('place_name')  # Extract the place name
    print(f"Place Tapped: {place_name}")  # Log the name of the tapped place
    # TODO: Perform any server-side action (e.g., store in database, etc.)

    _, updated_places = fetch_places_data()
    print(place_name, updated_places)
    mec.places_dict = {place_name: updated_places[place_name]}

    if user_id not in mec.convo.chat_histories.keys():
        print(f"creating chathistory for user {user_id}")
        mec.convo.chat_histories[user_id] = [{"role": "system", "content": f"Be an assistant and guide at {place_name}." + wrapper.DEFAULT_PROMPT},]
        print("\n\n\n\n\n/////////")
    
    #bot_response = executor.submit(mec.chat_api_v2, [user_id, "Hi"]).result()
    #logging.info(f'User ({user_id}): {"Hi"}, Bot: {bot_response}')

    # Responding back to the client
    return jsonify({"status": "success", "message": place_name}), 200

@app.route('/api/chat', methods=['POST'])
def chat_api_v2():
    try:
        user_id = request.json['user_id']  # Get the user ID
    except:
        print("no user id found")
        user_id = "anonymous"
    user_message = request.json['message']
    bot_response = executor.submit(mec.chat_api_v2, [user_id, user_message]).result()
    logging.info(f'User ({user_id}): {user_message}, Bot: {bot_response}')
    # Save the user's message and the bot's response to the database with user_id
    return jsonify({'message': bot_response})

def analyze_image(inputs):
    user_id, filename = inputs
    return mec.analyze_image_api(user_id, filename)

@app.route('/api/image', methods=['POST'])
def upload_image():
    file = request.files['file']
    # Check if no file is selected
    if not file or file.filename == '':
        return jsonify(success=False, error="No file selected"), 400
    
    user_id = "anonymous"

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    print(user_id, filename)
 
    sim_score, image_info, image_prompts = executor.submit(analyze_image, [user_id, filename]).result()
    to_sent = {'file_name':'something.jpeg','sim_score':sim_score, 'text':image_prompts}
    if sim_score:
        image_info['sim_score'] = sim_score
        image_info['text'] = image_prompts
        print(image_info)
        return jsonify(success=True, message=to_sent)
    else:
        return jsonify(success=True, message={"file_name": "N/A", "text": "Image not found in vector database!!!", "sim_score": None})

"""
class Message:
    def __init__(self, content, chatroom_id, timestamp, sender="user"):
        self.content = content
        self.chatroom_id = chatroom_id
        self.timestamp = timestamp
        self.sender = sender  # 'user' or 'bot'

@app.route('/api/messages', methods=['POST'])
def receive_message():
    # Get the multipart data
    contentType = request.form.get("contentType")
    content = request.form.get("content")
    image_file: FileStorage = request.files.get("imageData")
    audio_file: FileStorage = request.files.get("audioData")
    chatRoomID = request.form.get("chatRoomID")
    senderUserID = request.form.get("senderUserID")

    # Logging the received data for debugging
    if content:
        print(f"Received content: {content}")
    if image_file:
        print(f"Received image with filename: {image_file.filename}")
        # Save or process the image as needed
    if audio_file:
        print(f"Received audio with filename: {audio_file.filename}")
        # Save or process the audio as needed

    # Generate some fields for the response
    messageID = str(uuid4())  # Generate a unique message ID
    timestamp = datetime.utcnow()  # Current time
    status = "sent"  # Set the status as sent once received by the server

    # Construct the response based on MessageDTO
    response_data = {
        "messageID": messageID,
        "chatRoomID": chatRoomID,
        "senderUserID": chatRoomID,
        "contentType": contentType,
        "content": content,
        # Storing file paths for simplicity in this example. In a real-world scenario, you'd want to handle files differently.
        "imageData": f"/path/to/images/{image_file.filename}" if image_file else None,
        "audioData": f"/path/to/audios/{audio_file.filename}" if audio_file else None,
        "timestamp": timestamp.timestamp(),  # This will return the time in seconds since 1970
        "status": status
    }

    print(f"send back \n {response_data}")

    return jsonify(response_data) 
"""

if __name__ == '__main__':
    print("..........\n\n\n")
    app.run(host='0.0.0.0', port=9090, debug=True)





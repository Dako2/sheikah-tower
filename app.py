from flask import Flask, request, jsonify
from werkzeug.datastructures import FileStorage
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging
from llm.llm_agent import Conversation
import openai
from environment import OPENAI_API_KEY
import wrapper
import os

from uuid import uuid4

# Initialize executor and set workers
executor = ThreadPoolExecutor(max_workers=4)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set up Flask and logging
app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

openai.api_key = OPENAI_API_KEY
mec = wrapper.MECApp()

def fetch_chat_response(user_message):
    return mec.chat_api(user_message)

@app.route('/api/location', methods=['POST'])
def location_api(ip_addr = '10.10.0.1'):
    lat, lgn, _ = mec.loc_user_api(ip_addr)
    logging.info(f'Location: {lat}, {lgn}')
    return jsonify({'latitude': lat, 'longitude': lgn})

def fetch_places_data():
    return mec.loc_user_places_api()

@app.route('/api/places', methods=['POST'])
def places_api():
    (lat, lgn), nearby_locations = executor.submit(fetch_places_data).result()
    nearby_locations['user'] = {'latitude': lat, 'longitude': lgn,'db_path':''}
    logging.info(f'Nearby locations: {nearby_locations}')
    print({"message":{'latitude': lat, 'longitude': lgn, 'places': nearby_locations}})

    return jsonify({"message":{'latitude': lat, 'longitude': lgn, 'places': nearby_locations}})

@app.route('/api/chat', methods=['POST'])
def chat_api():
    user_message = request.json['message']
    bot_response = executor.submit(fetch_chat_response, user_message).result()
    logging.info(f'User: {user_message}, Bot: {bot_response}')
    return jsonify({'message': bot_response})

def analyze_image(filename):
    return mec.analyze_image_api(filename)

@app.route('/api/image', methods=['POST'])
def upload_image():
    file = request.files.get('file')

    if not file or file.filename == '':
        return jsonify(error="No file provided"), 400

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    sim_score, image_info, image_prompts = executor.submit(analyze_image, filename).result()
    to_sent = {'file_name':'something.jpeg','sim_score':sim_score, 'text':image_prompts}
    if sim_score:
        image_info['sim_score'] = sim_score
        image_info['text'] = image_prompts
        
        print(image_info)
        return jsonify(success=True, message=to_sent)
    else:
        return jsonify(success=True, message={"file_name": "N/A", "text": "Image not found in vector database!!!", "sim_score": None})


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

if __name__ == '__main__':
    print("..........\n\n\n")
    app.run(host='0.0.0.0', port=9090, debug=True)





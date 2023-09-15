from concurrent.futures import ThreadPoolExecutor
import logging
from flask import Flask, request, jsonify
from llm.llm_agent import Conversation
import openai
from environment import OPENAI_API_KEY
import wrapper
import os

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

@app.route('/api/chat', methods=['POST'])
def chat_api():
    user_message = request.json['message']
    bot_response = executor.submit(fetch_chat_response, user_message).result()
    logging.info(f'User: {user_message}, Bot: {bot_response}')
    return jsonify({'message': bot_response})

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
    logging.info(f'Nearby locations: {nearby_locations}')
    return jsonify({"message":{'latitude': lat, 'longitude': lgn, 'places': nearby_locations}})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)

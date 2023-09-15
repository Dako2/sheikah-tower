"""
app.py (frontend)
 |_wrapper.py (backend wrapper)
    |_ llm.llm_agent.py, mec_apis.mec_location_api.py, VecDB.py

"""
from concurrent.futures import ProcessPoolExecutor
import logging
import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
from llm.llm_agent import Conversation
import openai
from environment import OPENAI_API_KEY
import wrapper
import json
import os
import multiprocessing

executor = ProcessPoolExecutor(max_workers=4)  # Adjust max_workers based on your CPU cores

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

conversation = Conversation()  # An instance of the Conversation class to handle the chat.
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def chat():
    chat_history = "".join([f"<p><strong>{message['role'].capitalize()}:</strong> {message['content']}</p>" for message in conversation.messages])
    return render_template_string("""
        <html>
        <head>
        <title>OpenAI Chatbot</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <style>
            body {
                display: flex;
                flex-direction: column;
                height: 100vh;
                margin: 0;
            }

            #chatbox {
                flex: 1;
                overflow-y: auto;
                padding: 10px;
                border-bottom: 1px solid #ccc;
            }
        </style>
        </head>
        <body>
            <h1>Chat with OpenAI</h1>
            <div id="chatbox">
                {{ chat_history|safe }}
            </div>
            <form onsubmit="sendMessage(event)">
                <input type="text" name="message" id="messageInput" placeholder="Enter your message">
                <button type="submit">Send</button>
            </form>
            <script>
                var socket = io.connect('http://localhost:9090');
                
                socket.on('new message', function(data) {
                    var messageElement = document.createElement('p');
                    messageElement.innerHTML = '<strong>' + data.sender + ':</strong> ' + data.message;
                    var chatbox = document.getElementById('chatbox');
                    chatbox.appendChild(messageElement);
                    chatbox.scrollTop = chatbox.scrollHeight;
                });

                function sendMessage(event) {
                    event.preventDefault();
                    var inputElement = document.getElementById('messageInput');
                    var message = inputElement.value;
                    socket.emit('message sent', {'message': message});
                    inputElement.value = '';
                }
            </script>
        </body>
        </html>
    """, chat_history=chat_history)

@socketio.on('message sent')
def handle_message(data):
    user_message = data['message']
    logging.info(f'User sent message: {user_message}')
    emit('new message', {'sender': 'You', 'message': user_message}, broadcast=True)
    #bot_response = conversation.rolling_convo(user_message, None, None) #default
    bot_response = mec.chat_api(user_message) #vector database
    logging.info(f'Bot response: {bot_response}')
    emit('new message', {'sender': 'Bot', 'message': bot_response}, broadcast=True)

def fetch_chat_response(user_message):
    return mec.chat_api(user_message)
@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        # Get the user's message from the request's JSON data
        user_message = request.json['message']
        # Call the mec.chat_api function to get the bot's response
        future = executor.submit(fetch_chat_response, user_message)
        bot_response = future.result()
        # Log the user's message and bot's response
        logging.info(f'User sent message: {user_message}')
        logging.info(f'Bot response: {bot_response}')
        # Return the bot's response as JSON
        return jsonify({'message': bot_response})

    except Exception as e:
        # Handle any exceptions, e.g., invalid JSON format or errors in chat_api function
        logging.error(f'Error in chat_api: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500

mec = wrapper.MECApp()
@app.route('/api/location', methods=['POST'])
def location_api(ip_addr = '10.10.0.1'):
    try:
        # Get the location data from the request's JSON data

        lat, lgn, _ = mec.loc_user_api(ip_addr)
        # Log the received location data
        logging.info(f'Received location data: {lat}, {lgn}')
        return jsonify({'message': {"latitude":lat,"longitude":lgn}})

    except Exception as e:
        # Handle any exceptions, e.g., invalid JSON format or processing errors
        logging.error(f'Error in location_api: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500
    
def fetch_places_data():
    return mec.loc_user_places_api()
@app.route('/api/places', methods=['POST'])
def places_api():
    try:
        future = executor.submit(fetch_places_data)
        (lat, lgn), nearby_locations = future.result()
        
        logging.info(f'Received location data: {nearby_locations}')
        to_send = {"latitude": lat, "longitude": lgn, "places": nearby_locations}
        print("to_send", to_send)
        
        return jsonify({'message': to_send})

    except Exception as e:
        logging.error(f'Error in places_api: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500
    
def analyze_image(filename):
    return mec.analyze_image_api(filename)
@app.route('/api/image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify(error="No file part in the request"), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    if file:
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        print(f"received image and saved {filename}")

        # Analyze the image using a separate process
        print("analyzing the image ...")
        future = executor.submit(analyze_image, filename)
        sim_score, image_info = future.result()
        
        if sim_score:
            image_info['sim_score'] = sim_score    
            return jsonify(success=True, message=image_info), 200
        else:
            return jsonify(success=True, message={"file_name": "N/A", "text": "Not found the image in vector database","sim_score": None}), 200

if __name__ == '__main__':
    multiprocessing.set_start_method('fork')
    
    socketio.run(app, host='0.0.0.0',port=9090, debug=False)

"""
app.py (frontend)
 |_wrapper.py (backend wrapper)
    |_ llm.llm_agent.py, mec_apis.mec_location_api.py, VecDB.py

"""


import logging
import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
from llm.llm_agent import Conversation
import openai
from environment import OPENAI_API_KEY
import wrapper

conversation = Conversation()  # An instance of the Conversation class to handle the chat.
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
mec = wrapper.MECApp()

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

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        # Get the user's message from the request's JSON data
        user_message = request.json['message']

        # Call the mec.chat_api function to get the bot's response
        bot_response = mec.chat_api(user_message)

        # Log the user's message and bot's response
        logging.info(f'User sent message: {user_message}')
        logging.info(f'Bot response: {bot_response}')

        # Return the bot's response as JSON
        return jsonify({'message': bot_response})

    except Exception as e:
        # Handle any exceptions, e.g., invalid JSON format or errors in chat_api function
        logging.error(f'Error in chat_api: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/api/location_only', methods=['POST'])
def location_api(ip_addr = '10.100.0.4'):
    try:
        # Get the location data from the request's JSON data
        location_data = mec.loc_user_api(ip_addr)
        # Log the received location data
        logging.info(f'Received location data: {location_data}')
        # Return a response as needed (e.g., success message or processed data)
        response_message = "Location data received and processed successfully"
        return jsonify({'message': location_data})

    except Exception as e:
        # Handle any exceptions, e.g., invalid JSON format or processing errors
        logging.error(f'Error in location_api: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/api/location', methods=['POST']) #get the json file of the places of interest
def location_api(ip_addr = '10.100.0.4'):
    try:
        # Get the location data from the request's JSON data
        user_live_coor, nearby_locations, event = mec.loc_api(radius = 1000)
        # Log the received location data
        logging.info(f'Received location data: {nearby_locations}')
        # Return a response as needed (e.g., success message or processed data)
        response_message = "Location data received and processed successfully"
        return jsonify({'message': nearby_locations})

    except Exception as e:
        # Handle any exceptions, e.g., invalid JSON format or processing errors
        logging.error(f'Error in location_api: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port=9090, debug=False)

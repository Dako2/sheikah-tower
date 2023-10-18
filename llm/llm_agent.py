import openai
import datetime

class Conversation:
    def __init__(self):

        #if spot_mode, just append to this system messages
        #self.PROMPT_LIST = [{"desert_mode":"Be a helpful tour guide and language interpreter."}]
        self.messages = [{"role": "system", "content": "Be a helpful tour guide"},]
        self.chat_histories = {"anonymous":self.messages}

    def call_api(self, user_id, messages):
        print(f"\n[userid: {user_id}] To ChatGPT ", messages)
        # text + user inputs as inputs of calling LLM APIs
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages = messages,
            max_tokens=500,
            temperature=1.2 #0.4 More parameters can be added if necessary
            # presence_penalty=0, frequency_penalty=0 # [-2~2]
        )

        # Get response from calling the API
        completion = response['choices']
        message = completion[-1]['message']['content']

        print(response['usage'])
        print(message)

        return message
        # TODO: Add logic to calculate tokens used and speed

    def rolling_convo(self, user_id, user_input, found_db_texts, found_db_user_data, user_location_info = None):
        
        if user_id not in self.chat_histories.keys():
            print(f"creating chathistory for user {user_id}")
            self.chat_histories[user_id] = [{"role": "system", "content": "Be a helpful assistant"},]

        # Append the user's message and bot's response
        messages = self.chat_histories[user_id]

        messages.append({"role": "user", "content": user_input})
        vec_info = ''
        if found_db_texts:
            messages.append({"role": "system", "content": f"Found some local knowledge: {found_db_texts}"})
            #vec_info = f'\n<p style="color: red;">found local info: {found_db_texts}</p>\n'
            vec_info = f'\n\n === found local vectdata === \n{found_db_texts}\n'
        
        if found_db_user_data:
            messages.append({"role": "system", "content": f"{found_db_user_data}"})
        #    vec_info = f'\n<p style="color: red;">found user info: {found_db_user_data}</p>\n'
        
        chat_response = self.call_api(user_id, messages) # use new added user_input to call API again
        if messages[-1]["role"] == "system": #TODO more robust removing "found local knowledge" to keep token size small
            messages = messages[:-1]

        # shall we append assistant role? @yihan
        messages.append({"role": "assistant", "content": chat_response}) #['system', 'assistant', 'user', 'function']
        
        self.chat_histories[user_id] = messages

        return chat_response + vec_info
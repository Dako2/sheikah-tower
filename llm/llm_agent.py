import openai

class Conversation:
    def __init__(self):
        
        #if spot_mode, just append to this system messages
        #self.PROMPT_LIST = [{"desert_mode":"Be a helpful tour guide and language interpreter."}]
        self.messages = [{"role": "system", "content": "Be a helpful tour guide"},]
    
    def call_api(self):
        print("\n\n To_ChatGPT",self.messages)
        # text + user inputs as inputs of calling LLM APIs
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=self.messages,
            max_tokens=4000,
            temperature=1.5 #0.4 More parameters can be added if necessary
            # presence_penalty=0, frequency_penalty=0 # [-2~2]
        )

        # Get response from calling the API
        completion = response['choices']
        message = completion[-1]['message']['content']

        print(response['usage'])

        return message
        # TODO: Add logic to calculate tokens used and speed
   
    def rolling_convo(self, user_input, found_db_texts, found_db_user_data, user_location_info = None):
        self.messages.append({"role": "user", "content": user_input})
        vec_info = ''
        if found_db_texts:
            self.messages.append({"role": "assistant", "content": f"Found some local knowledge: {found_db_texts}"})
            #vec_info = f'\n<p style="color: red;">found local info: {found_db_texts}</p>\n'
            vec_info = f'\n\n === found local vectdata === \n{found_db_texts}\n'

        #if found_db_user_data:
        #    self.messages.append({"role": "system", "content": f"The virtual user info: {found_db_user_data}"})
        #    vec_info = f'\n<p style="color: red;">found user info: {found_db_user_data}</p>\n'
        
        chat_response = self.call_api() # use new added user_input to call API again
        self.messages = self.messages[:-1]
        # shall we append assistant role? @yihan
        self.messages.append({"role": "assistant", "content": chat_response}) #['system', 'assistant', 'user', 'function']
        
        return chat_response + vec_info
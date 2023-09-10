import openai

class Conversation:
    def __init__(self):
        self.messages = [{"role": "system", "content": "Be a helpful assitant and language interpreter for Monoco."},{"role": "assistant", "content": "Hi Link!"}]
    def call_api(self):
        # text + user inputs as inputs of calling LLM APIs
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=self.messages,
            max_tokens=200,
            temperature=0.4  # More parameters can be added if necessary
            # presence_penalty=0, frequency_penalty=0 # [-2~2]
        )

        # Get response from calling the API
        completion = response['choices']
        message = completion[-1]['message']['content']
        return message
        # TODO: Add logic to calculate tokens used and speed
   
    def rolling_convo(self, user_input, found_db_texts, found_db_user_data, user_location_info = None):
        self.messages.append({"role": "user", "content": user_input})
        vec_info =''
        if found_db_texts:
            self.messages.append({"role": "system", "content": f"Some helpful knowledge: {found_db_texts}"})
            vec_info = f'\n<p style="color: red;">found loc info: {found_db_texts}</p>'

        if found_db_user_data:
            self.messages.append({"role": "system", "content": f"Something you know about the user: {found_db_user_data}"})
            vec_info = f'\n<p style="color: red;">found user info: {found_db_user_data}</p>'

        if user_location_info: # @QT new added
            self.messages.append({"role": "system", "content": f"User is near: {user_location_info}"})
            vec_info = f'\n<p style="color: red;">found user info: {user_location_info}</p>'
    
        chat_response = self.call_api() # use new added user_input to call API again
        print(f"\n\nVIP Guide: {chat_response}")
        self.messages.append({"role": "assistant", "content": chat_response}) #['system', 'assistant', 'user', 'function']
        
        return chat_response + vec_info
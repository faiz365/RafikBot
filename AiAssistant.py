import openai
import time
import tiktoken
import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAIAPIKEY")
authorization = os.getenv("AUTHORIZATION")
xuser_id = os.getenv("X-USER-ID")
max_response_tokens = 250
token_limit = 4096


class RafikService:
    conversation = []

    def __init__(self):
        self.conversation = [{"role": "system", "content": "You are a helpful assistant named Rafik"}]

    @classmethod
    def num_tokens_from_messages(cls, messages):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0301")
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    @classmethod
    def generate_response(cls, text, language):
        user_input = text
        cls.conversation.append({"role": "system",
                                 "content": f"act like normal human and your response must be in {language} and any other language is forbidden!!!!"})
        cls.conversation.append({"role": "user", "content": user_input})
        conv_history_tokens = cls.num_tokens_from_messages(cls.conversation)
        print("previous =", conv_history_tokens)
        while conv_history_tokens + max_response_tokens >= token_limit:
            del cls.conversation[1]
            conv_history_tokens = cls.num_tokens_from_messages(cls.conversation)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=cls.conversation,
            temperature=1,
            max_tokens=max_response_tokens,
            top_p=0.9
        )
        cls.conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        return str(response['choices'][0]['message']['content'])

    @classmethod
    def from_speech_to_text(cls, filename):
        audio_file = open(f"UserVoiceMessages/{filename}.wav", "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript.text

    @classmethod
    def speech_to_text(cls, filename,language ):
        user_text = cls.from_speech_to_text(filename)
        bot_text = cls.generate_response(user_text,language=language)
        return bot_text

    @classmethod
    def text_to_speech(cls, userid, text, language):
        act = ""
        if language == "english":
           act = "Matthew"
        else:
            act = "ar-XA-Standard-C"
        bot_text = cls.generate_response(text, language)

        return cls.get_bot_voice(bot_text, userid, act)

    @classmethod
    def speech_to_speech(cls, userid, language):
        act = ""
        if language == "english":
            act = "Matthew"
        else:
            act = "ar-XA-Standard-C"
        user_text = cls.from_speech_to_text(userid)
        bot_text = cls.generate_response(user_text, language)
        print(bot_text)
        return cls.get_bot_voice(bot_text, userid, act)




    @classmethod
    def get_bot_voice(cls, bot_text, userid, actor):
        url = "https://play.ht/api/v1/convert"
        my_list = []
        # Generate and send voice messages for each sentence
        # Generate the speech
        payload = {
            "content": [bot_text],
            "voice": actor

        }
        print(actor)
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "AUTHORIZATION": authorization,
            "X-USER-ID": xuser_id
        }
        time.sleep(4)
        response = requests.post(url, json=payload, headers=headers)
        print(response.status_code)
        if response.status_code != 201:
            return []

        json_data = json.loads(response.text)
        transcription_id = json_data['transcriptionId']
        url = f"https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}"
        headers = {
            "accept": "application/json",
            "AUTHORIZATION": "2809beb29a5645459aa3e9bd1951322f",
            "X-USER-ID": "9lIoL4AhRvf9pIiiVhUk8GuTz2w1"
        }
        time.sleep(4)
        response = requests.get(url, headers=headers)

        json_data = json.loads(response.text)
        audio = json_data['audioUrl']
        response = requests.get(f'{audio}')
        time.sleep(1)

        if response.status_code == 200:
            with open(f"BotVoiceMessages/message{userid}.mp3", "wb") as f:
                f.write(response.content)

        my_list.append(f'message{userid}.mp3')
        # Send voice message to user
        # Wait for 1 second before sending the list
        time.sleep(1)
        return my_list

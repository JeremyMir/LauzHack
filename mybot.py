import telebot
from keys import TELEGRAM_KEY, HUGGING_FACE_KEY
import logging
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import requests
import json


#=========LOGGER=========
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

#==========The Bot=========
class Speech2TextBot(telebot.TeleBot):
    def __init__(self, apikey):
        super().__init__(apikey)
        self.activation = True

    def change_activate(self):
        self.activation = not self.activation

    
bot = Speech2TextBot(TELEGRAM_KEY)

#==========Welcome=========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome!")

#=========Commands=========
bot.set_my_commands([
        telebot.types.BotCommand("/activate", "Activate/Deactivate the bot."),
        telebot.types.BotCommand("/generate", "Jouer avec gpt2")
        ])

#=========Activation=======
@bot.message_handler(commands=['activate'])
def activate(message):
    status_string = "activated" if bot.activation else "not activated"
    on_button = "Disactivate bot" if bot.activation else "Activate bot"
    bot.send_message(message.chat.id, f"The bot is currently {status_string}.", reply_markup=make_activation_button(on_button=on_button))

def make_activation_button(on_button:str):
    button = telebot.types.InlineKeyboardButton(text=on_button, callback_data="activation")
    markup = telebot.types.InlineKeyboardMarkup(row_width=1).add(button)
    return markup

@bot.callback_query_handler(func= lambda call: call.data=="activation")
def change_activation(call):
    bot.change_activate()
    activate_string = "activated" if bot.activation else "disactivated"
    bot.send_message(call.message.chat.id, f"The bot has been {activate_string}.")

#=========Weird shit with huggingface==========
headers = {"Authorization": f"Bearer {HUGGING_FACE_KEY}"}
API_URL = "https://api-inference.huggingface.co/models/openai-community/gpt2-large"

parameters = {
    "max_new_tokens": 50  
}

def generate_answer(payload):
    response = requests.post(
    API_URL, 
    headers=headers, 
    json = payload
    )
    return response.json()

payload1 = {
    "inputs": "Can you please let us know more details about your ",
    "parameters": parameters
}

outs = generate_answer(payload1)
print(outs)

@bot.message_handler(commands=['generate'])
def generate(message):
    text = message.text[9:]
    bot.send_message(message.chat.id, f"Your message is:{text}.")
    payload = {
        "inputs": text,
        "parameters":parameters
    }
    out = generate_answer(payload=payload)
    bot.send_message(message.chat.id, out[0]['generated_text'])

#===========Speech2Text===============
#API_URL_S2T = "https://api-inference.huggingface.co/models/facebook/wav2vec2-base-960h"
API_URL_S2T = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.request("POST", API_URL_S2T, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

def query_with_file(file):
    data=file.read()
    response = requests.request("POST", API_URL_S2T, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

sample_audio = "sample2.wav"

audio_out = query(sample_audio)
print(audio_out)

@bot.message_handler(content_types=['voice'])
def handle_docs_audio(message):
    
    audio_file = bot.get_file(message.voice.file_id)
    #audio_out = query_with_file(audio_file)
    file_path = 'temp_audio.ogg'
    downloaded_file = bot.download_file(audio_file.file_path)
    with open(file_path,'wb') as new_file:
        new_file.write(downloaded_file)
    audio_out = query("temp_audio.ogg")
    print(audio_out)
    bot.send_message(message.chat.id, audio_out['text'])

#==========Polling=========
bot.infinity_polling()
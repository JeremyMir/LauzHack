
from keys import TELEGRAM_KEY, HUGGING_FACE_KEY
import logging
#from transformers import GPT2LMHeadModel, GPT2Tokenizer
import requests
import json
import math
from pydub import AudioSegment
import telebot
#import librosa


#=========LOGGER=========
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

#========Header for huggingface=============
headers = {"Authorization": f"Bearer {HUGGING_FACE_KEY}"}

#==========The Bot=========
class Speech2TextBot(telebot.TeleBot):
    def __init__(self, apikey):
        super().__init__(apikey)
        self.activation = True
        self.family_friendly = False
        self.paraphraser = True

    def change_activate(self):
        self.activation = not self.activation

    def change_family_friendly(self):
        self.family_friendly = not self.family_friendly

    def change_paraphraser(self):
        self.paraphraser = not self.paraphraser
    
bot = Speech2TextBot(TELEGRAM_KEY)

#===========Decorators============
def do_if_activated(func):
    def if_activated(message):
        if bot.activation:
            return func(message)
        else:
            pass
    return if_activated

def block_if_profane(func):
    def if_profane(message, text):
        if bot.family_friendly:
            if IsProfane(text):
                bot.send_message(message.chat.id, "If you have nothing nice to say, don't say anything.")
            else:
                return func(message, text)
        else:
            return func(message, text)
    return if_profane

def IsProfane(text:str)->bool:
    API_URL_PROFANE = "https://api-inference.huggingface.co/models/tarekziade/pardonmyai"
    payload = {
        "inputs":text
    }
    response = requests.post(API_URL_PROFANE, headers=headers, json=payload)
    print(response.json())
    scores = response.json()
    if (scores[0][0]['score']<0.3 and scores[0][0]['label']=='NOT_OFFENSIVE') or (scores[0][0]['score']>0.7 and scores[0][0]['label']=='OFFENSIVE'):
        return True
    else:
        return False


#==========Welcome=========
@bot.message_handler(commands=['start'])
@do_if_activated
def start(message):
    bot.send_message(message.chat.id, "Welcome!")

#=========Commands=========
bot.set_my_commands([
        telebot.types.BotCommand("/activate", "Activate/Deactivate the bot."),
        telebot.types.BotCommand("/generate", "Jouer avec gpt2"), 
        telebot.types.BotCommand("/family_friendly", "Filter out profane audio messages.")
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

#==========Family Friendly=================
@bot.message_handler(commands=['family_friendly'])
def fam_friendly(message):
    status_string = "family friendly" if bot.family_friendly else "uncensored"
    on_button = "Turn off family friendly mode" if bot.family_friendly else "Turn on family friendly mode"
    bot.send_message(message.chat.id, f"The bot is currently {status_string}.", reply_markup=make_family_button(on_button=on_button))

def make_family_button(on_button:str):
    button = telebot.types.InlineKeyboardButton(text=on_button, callback_data="pg-13")
    markup = telebot.types.InlineKeyboardMarkup(row_width=1).add(button)
    return markup

@bot.callback_query_handler(func= lambda call: call.data=="pg-13")
def change_family(call):
    bot.change_family_friendly()
    friendly_string = "family friendly" if bot.family_friendly else "uncensored"
    bot.send_message(call.message.chat.id, f"The bot is now {friendly_string}.")

#=============Paraphrasing======================
@bot.message_handler(commands=['paraphrase'])
def paraphrase_on(message):
    status_string = "on" if bot.paraphraser else "off"
    on_button = "Turn off paraphraser" if bot.paraphraser else "Turn on paraphraser"
    bot.send_message(message.chat.id, f"The paraphraser is currently {status_string}.", reply_markup=make_paraphrase_button(on_button=on_button))

def make_paraphrase_button(on_button:str):
    button = telebot.types.InlineKeyboardButton(text=on_button, callback_data="summary")
    markup = telebot.types.InlineKeyboardMarkup(row_width=1).add(button)
    return markup

@bot.callback_query_handler(func= lambda call: call.data=="summary")
def change_family(call):
    bot.change_paraphraser()
    paraphrase_string = "on" if bot.paraphraser else "off"
    bot.send_message(call.message.chat.id, f"The paraphraser is now {paraphrase_string}.")

#=========Weird shit with huggingface==========

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
@do_if_activated
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
def query(filename, num_parts:int, length:float):
    '''with open(filename, "rb") as f:
        data = f.read()
        print(type(data))
        print(len(data))
    slice = len(data)/num_parts'''
    return_str = ''
    audio = AudioSegment.from_ogg(filename)
    slice = len(audio)//num_parts
    for part in range(int(num_parts)):
        print(f'part {part} of {num_parts}')
        print(slice)
        print(part)
        audio_slice=audio[slice*part:slice*(part+1)]
        audio_slice.export("temp_slice.wav", format="wav")
        with open("temp_slice.wav", 'rb') as f:
            data_=f.read()
        response = requests.request("POST", API_URL_S2T, headers=headers, data=data_)
        output = json.loads(response.content.decode("utf-8"))
        if 'error' in output:
            print(output)
            if num_parts > math.ceil(length/10)+2:
                return False
            else:
                return query(filename, int(num_parts)+1, length)
        return_str += output['text']
    return return_str

'''def query_with_file(file):
    data=file.read()
    response = requests.request("POST", API_URL_S2T, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))'''

'''sample_audio = "sample2.wav"

audio_out = query(sample_audio, 1, 3)
print(audio_out)'''

#============Check for profanity=================
@block_if_profane
def send_text(message, text):
    bot.send_message(message.chat.id, text)

#===========Speech2Text (suite)===============

@bot.message_handler(content_types=['voice'])
@do_if_activated
def handle_docs_audio(message):
    length = message.voice.duration
    audio_file = bot.get_file(message.voice.file_id)
    file_path = 'temp_audio.ogg'
    downloaded_file = bot.download_file(audio_file.file_path)
    with open(file_path,'wb') as new_file:
        new_file.write(downloaded_file)
    #length = librosa.get_duration(filename='temp_audio.ogg')
    num_parts=math.ceil(length/25)
    text = query("temp_audio.ogg", num_parts, length)
    if text==False:
        bot.send_message(message.chat.id, "An error occured.")
    else:
        if len(text.split())>100 and bot.paraphraser:
            text = paraphrase(text)
        print(text)
        send_text(message, text)

#==============Paraphrasing============================
def paraphrase(text:str)->str:
    #Input: some text
    #Ouput: a summary of the input
    API_URL_PARAPHRASE = "https://api-inference.huggingface.co/models/humarin/chatgpt_paraphraser_on_T5_base"
    payload = {
        "inputs":text
    }
    response = requests.post(API_URL_PARAPHRASE, headers=headers, json=payload)
    return response.json()[0]['generated_text']

    

#==========Polling=========
bot.infinity_polling()
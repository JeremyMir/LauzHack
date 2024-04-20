import telebot
from keys import TELEGRAM_KEY, HUGGING_FACE_KEY
import logging
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
import requests
import json
import whisper_timestamped as whisper


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

    def change_activate(self):
        self.activation = not self.activation

    def change_family_friendly(self):
        self.family_friendly = not self.family_friendly

    
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
    def if_profane(message, audio_out):
        if bot.family_friendly:
            if IsProfane(audio_out['text']):
                bot.send_message(message.chat.id, "If you have nothing nice to say, don't say anything.")
            else:
                return func(message, audio_out)
        else:
            return func(message, audio_out)
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
def activate(message):
    status_string = "family friendly" if bot.family_friendly else "uncensored"
    on_button = "Turn off family friendly mode" if bot.family_friendly else "Turn on family friendly mode"
    bot.send_message(message.chat.id, f"The bot is currently {status_string}.", reply_markup=make_activation_button(on_button=on_button))

def make_activation_button(on_button:str):
    button = telebot.types.InlineKeyboardButton(text=on_button, callback_data="pg-13")
    markup = telebot.types.InlineKeyboardMarkup(row_width=1).add(button)
    return markup

@bot.callback_query_handler(func= lambda call: call.data=="pg-13")
def change_activation(call):
    bot.change_family_friendly()
    activate_string = "family friendly" if bot.family_friendly else "uncensored"
    bot.send_message(call.message.chat.id, f"The bot is now {activate_string}.")

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
def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.request("POST", API_URL_S2T, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

def query_with_file(file):
    data=file.read()
    response = requests.request("POST", API_URL_S2T, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

# sample_audio = "sample2.wav"
# audio_out = query(sample_audio)
# print(audio_out)

@block_if_profane
def send_text(message, audio_out):
    bot.send_message(message.chat.id, audio_out['text'])

@bot.message_handler(content_types=['voice'])
@do_if_activated
def handle_docs_audio(message):
    audio_file = bot.get_file(message.voice.file_id)
    #audio_out = query_with_file(audio_file)
    file_path = 'temp_audio.ogg'
    downloaded_file = bot.download_file(audio_file.file_path)
    with open(file_path,'wb') as new_file:
        new_file.write(downloaded_file)
    # audio_out = query("temp_audio.ogg")
    # print("------------------")
    # print("audio_out", audio_out)
    # print("------------------")
    # send_text(message, audio_out)
    audio = whisper.load_audio("temp_audio.ogg")
    model = whisper.load_model("tiny")
    result = whisper.transcribe(model, audio)
    
    word_time_pairs = []
    for segment in result['segments']:
        for word in segment['words']:
            word_time_pairs.append({"text": word['text'], "start":word['start']})
    # print(word_time_pairs)
    output = "Time\tText"
    for index, word in enumerate(word_time_pairs):
        if (index % 5) == 0:
            output += "\n" + str(word['start']) + "\t"
        output += word['text'] + " "
        
    print("result", result)
    print("------------------")
    print(json.dumps(result, indent = 2, ensure_ascii = False))
    print("------------------")
    send_text(message, {"text":output})

#==========Polling=========
bot.infinity_polling()
import telebot
from keys import TELEGRAM_KEY
import logging


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

#==========Polling=========
bot.infinity_polling()
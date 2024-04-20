# Intro
Everyone has that annoying friend who sends voice messages all the time. Well now, our bot will solve this for you!

## Installation

# 1) create and activate virtual environment
# -- EITHER with conda
conda create -n apis_env python=3.11
conda activate apis_env
# 2) install dependencies
(apis_env) pip3 install -r requirements.txt

# Transcriptor
The bot detects voice messages and transcribes them into text.

## Options
- Activation: you can activate or deactivate the bot with the command _/activate_.
- Family friendly: you instruct the bot not to transcribe messages containing profanities. This option can be toggled on or off with the command _/family_friendly_.
- Paraphraser: the bot will summarise messages that are more than 100 words long. This option can also be toggled on or off using the command _/paraphrase_.

# To run the bot
Execute mybot.py after creating a keys.py file containing two string variables _TELEGRAM_KEY_ and _HUGGING_FACE_KEY_ containing the corresponding keys.

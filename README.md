# Bot transcirbing voice messages 
## Intro
Everyone has that annoying friend that sends way too long voice messages. Using our bot voice messages will be automatically transcribed into text. 
## Installation
1) Create and activate virtual environment
   ```
   conda create -n apis_env python=3.11
   conda activate apis_env
   ```
3) Install dependencies
   ```
   (apis_env) pip3 install -r requirements.txt
   ```
## To run the bot
1) Create your own Telegram Bot Key and Hugging face key
2) Create a keys.py file with your keys. Example:
   ```
   TELEGRAM_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   HUGGING_FACE_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```
3) Run the bot
   ```
   python mybot.py
   ```
## Options
- Activation: you can activate or deactivate the bot with the command _/activate_.
- Family friendly: you instruct the bot not to transcribe messages containing profanities. This option can be toggled on or off with the command _/family_friendly_.
- Paraphraser: the bot will summarise messages that are more than 100 words long. This option can also be toggled on or off using the command _/paraphrase_.

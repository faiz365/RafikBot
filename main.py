import telebot
from telebot import types, util
from pydub import AudioSegment
import time
from AiAssistant import RafikService
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
session_opened = {}
sessions_start_time = {}
os.system("sh test.sh")
print("start")
text = ""
@bot.message_handler(commands=["start", "menu", "close"])
def startBot(message):
    chat_id = message.chat.id
    if message.text == "/start":
        bot.send_message(chat_id, "Hello I'm Rafik! Please click here to Start /menu")

    elif message.text == "/menu":
        # Create the inline keyboard markup
        markup = types.InlineKeyboardMarkup()
        sts_button = types.InlineKeyboardButton("STS", callback_data="sts")
        tts_button = types.InlineKeyboardButton("TTS", callback_data="tts")
        stt_button = types.InlineKeyboardButton("STT", callback_data="stt")
        markup.row(sts_button)
        markup.row(tts_button)
        markup.row(stt_button)
        # Send the services message with the inline keyboard
        bot.send_message(chat_id, "Welcome! Please select an option:", reply_markup=markup)
    elif message.text == "/close":
        if chat_id in sessions_start_time:
            del sessions_start_time[chat_id]
            print("hello")
        if str(chat_id) + "#1" in session_opened:
            del session_opened[str(chat_id) + "#1"]
        if str(chat_id) + "#2" in session_opened:
            del session_opened[str(chat_id) + "#2"]
        if str(chat_id) + "#3" in session_opened:
            del session_opened[str(chat_id) + "#3"]
        bot.send_message(chat_id, "Session closed succesfuly")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == "sts":
        bot.send_message(call.message.chat.id,
                         "You selected STS. when you send voice message \"Rafik\" will replay also with voice message")
        ops_button = types.InlineKeyboardButton("OpenSession", callback_data="ops1")
        # Create the inline keyboard markup
        markup = types.InlineKeyboardMarkup()
        markup.row(ops_button)
        bot.send_message(call.message.chat.id, "Open Session here:", reply_markup=markup)

    elif call.data == "tts":
        bot.send_message(call.message.chat.id,
                         "You selected TTS. when you send a text \"Rafik\" will replay with a voice message ")
        ops_button = types.InlineKeyboardButton("OpenSession", callback_data="ops2")
        # Create the inline keyboard markup
        markup = types.InlineKeyboardMarkup()
        markup.row(ops_button)
        bot.send_message(call.message.chat.id, "Open Session here:", reply_markup=markup)
    elif call.data == "stt":
        bot.send_message(call.message.chat.id,
                         "You selected STT.when you send a voice message \"Rafik\" will replay with a text message")
        ops_button = types.InlineKeyboardButton("OpenSession", callback_data="ops3")
        # Create the inline keyboard markup
        markup = types.InlineKeyboardMarkup()
        markup.row(ops_button)
        bot.send_message(call.message.chat.id, "Open Session here:", reply_markup=markup)
    elif call.data == "ops1":
        user_id = call.message.chat.id
        print(user_id)
        if (str(user_id) + "#1") in session_opened or (str(user_id) + "#2") in session_opened or (
                str(user_id) + "#3") in session_opened:
            bot.send_message(user_id, "you already have an session opened")
        else:
            session_opened[str(user_id) + "#1"] = RafikService()
            sessions_start_time[user_id] = time.time()

            bot.send_message(user_id, " STS session has been opened")
    elif call.data == "ops2":
        user_id = call.message.chat.id
        print(user_id)
        if (str(user_id) + "#1") in session_opened or (str(user_id) + "#2") in session_opened or (
                str(user_id) + "#3") in session_opened:
            bot.send_message(user_id, "you already have an session opened")
        else:
            session_opened[str(user_id) + "#2"] = RafikService()
            sessions_start_time[user_id] = time.time()

            bot.send_message(user_id, " TTS session has been opened")
    elif call.data == "ops3":
        user_id = call.message.chat.id
        print(user_id)
        if (str(user_id) + "#1") in session_opened or (str(user_id) + "#2") in session_opened or (
                str(user_id) + "#3") in session_opened:
            bot.send_message(user_id, "you already have an session opened")
        else:
            session_opened[str(user_id) + "#3"] = RafikService()
            sessions_start_time[user_id] = time.time()
            bot.send_message(user_id, "STT session has been opened")
    elif call.data == "arabic":
        if os.path.exists(f'UserVoiceMessages/{call.message.chat.id}.wav'):
            handle_language(user_id=call.message.chat.id, language="arabic")
        else:
            bot.send_message(call.message.chat.id, "you didn't send an message")
    elif call.data == "english":
        print()
        if os.path.exists(f'UserVoiceMessages/{call.message.chat.id}.wav'):
            handle_language(user_id=call.message.chat.id,language="english")
        else:
            bot.send_message(call.message.chat.id,"you didn't send an message")




@bot.message_handler(content_types=["voice"])
def handle_voice_message(message):
    user_id = message.chat.id
    rafik_sts = session_opened.get(str(user_id) + "#1")
    rafik_stt = session_opened.get(str(user_id) + "#3")
    # Check if the user has a voice session opened
    if rafik_sts:
        voice_handler(message)
        # Create the inline keyboard markup
        markup = types.InlineKeyboardMarkup()
        ar_button = types.InlineKeyboardButton("Arabic", callback_data="arabic")
        en_button = types.InlineKeyboardButton("English", callback_data="english")
        markup.row(ar_button, en_button)
        # Send the language message with the inline keyboard
        bot.send_message(user_id, "Welcome! Please select an language:", reply_markup=markup)

    elif rafik_stt:
        voice_handler(message)
        # Create the inline keyboard markup
        markup = types.InlineKeyboardMarkup()
        ar_button = types.InlineKeyboardButton("Arabic", callback_data="arabic")
        en_button = types.InlineKeyboardButton("English", callback_data="english")
        markup.row(ar_button, en_button)
        # Send the language message with the inline keyboard
        bot.send_message(user_id, "Welcome! Please select an language:", reply_markup=markup)

    else:
        bot.send_message(user_id, "You do not have a voice session opened.")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    global text
    userid = message.chat.id
    rafik_tts = session_opened.get(str(userid) + "#2")
    if rafik_tts:
        text = message.text
        markup = types.InlineKeyboardMarkup()
        ar_button = types.InlineKeyboardButton("Arabic", callback_data="arabic")
        en_button = types.InlineKeyboardButton("English", callback_data="english")
        markup.row(ar_button, en_button)
        # Send the language message with the inline keyboard
        bot.send_message(userid, "Welcome! Please select an language:", reply_markup=markup)
    else:
        bot.send_message(userid, "You do not have a voice session opened.")

def handle_language(user_id, language):
    rafik_sts = session_opened.get(str(user_id) + "#1")
    rafik_tts = session_opened.get(str(user_id) + "#2")
    rafik_stt = session_opened.get(str(user_id) + "#3")
    if rafik_sts:
        mylist = rafik_sts.speech_to_speech(user_id,language)
        if not mylist:
            bot.send_message(user_id, 'a problem appear please forward your message')
            return
        bot.send_message(user_id, "The Voice Message Completed!")
        os.remove(f'UserVoiceMessages/{user_id}.wav')
        os.remove(f'UserVoiceMessages/{user_id}.ogg')
        for item in mylist:
           # Open the audio file and send it as a voice message
           with open(f'BotVoiceMessages/{item}', "rb") as audio_file:
              bot.send_voice(user_id, audio_file)
        for item in mylist:
          # remove bot files
          os.remove(f'BotVoiceMessages/{item}')
    elif rafik_tts:
        mylist = rafik_tts.text_to_speech(user_id, text, language)
        for item in mylist:
            # Open the audio file and send it as a voice message
            with open(f'BotVoiceMessages/{item}', "rb") as audio_file:
                bot.send_voice(user_id, audio_file)
        for item in mylist:
            os.remove(f'BotVoiceMessages/{item}')
    elif rafik_stt:
        bot_text = rafik_stt.speech_to_text(user_id, language)
        bot.send_message(user_id, "The Text Message Completed!")
        os.remove(f'UserVoiceMessages/{user_id}.wav')
        os.remove(f'UserVoiceMessages/{user_id}.ogg')
        bot.send_message(user_id, bot_text)



def voice_handler(message):
    userid = message.chat.id
    # get voice message file_id
    file_id = message.voice.file_id

    # get voice message file path
    file_path = bot.get_file(file_id).file_path

    # download voice message
    voice_file = bot.download_file(file_path)
    directory = 'UserVoiceMessages'
    # save voice message as OGG file
    ogg_file_path = os.path.join(directory, f'{userid}.ogg')
    with open(ogg_file_path, 'wb') as f:
        f.write(voice_file)
    # Load the OGG file
    ogg_file = AudioSegment.from_file(ogg_file_path, format="ogg")

    # Export the WAV file
    wav_file_path = os.path.join(directory, f'{userid}.wav')
    wav_file = ogg_file.export(wav_file_path, format="wav")
    while not os.path.exists(wav_file_path):
        time.sleep(1)
    # send confirmation message
    bot.send_message(userid, "Your Voice saved successfully")


bot.infinity_polling(allowed_updates=util.update_types)

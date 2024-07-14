import os
import telebot

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)


def send_notification(message):
    bot.send_message(CHAT_ID, message)

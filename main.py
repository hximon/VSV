from telethon import TelegramClient, events
from dotenv import load_dotenv
import os, ast
load_dotenv()

# 1. Get these from https://my.telegram.org
api_id = os.getenv('API_ID')  # your api_id
api_hash = os.getenv('API_HASH')  # your api_hash
bot_username = os.getenv("BOT_USERNAME")   # your bot username
channels_raw = os.getenv("TARGET_CHANNEL_IDS")
TARGET_CHANNEL_IDS = ast.literal_eval(channels_raw)

client = TelegramClient('forwarder_session', api_id, api_hash)

@client.on(events.NewMessage(chats=TARGET_CHANNEL_IDS))
async def handler(event):
    
    await client.forward_messages(bot_username, event.message)
    print("✅ Message forwarded!")

print("🚀 Listening for new messages in:", TARGET_CHANNEL_IDS)
client.start()
client.run_until_disconnected()

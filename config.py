import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('PEPWM_BOT_API_ID')
API_HASH = os.getenv('PEPWM_BOT_API_HASH')
BOT_TOKEN = os.getenv('PEPWM_BOT_BOT_TOKEN')
ALLOWED_CHATS = os.getenv('PEPWM_ALLOWED_CHATS').split(',')
WORKING_CHAT = os.getenv('WORKING_CHAT')
DEVELOPER_ID = os.getenv('DEVELOPER_ID')

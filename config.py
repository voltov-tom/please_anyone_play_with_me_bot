import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('PEPWM_BOT_API_ID')
API_HASH = os.getenv('PEPWM_BOT_API_HASH')
BOT_TOKEN = os.getenv('PEPWM_BOT_BOT_TOKEN')

WAR_CRY = [
    'Только псина не стреляет во вражину!',
    'Давай ебашить!',
    'Время убивать!',
    'Нужно больше комрадов!',
    'Пиво, девки, Валорант!',
    'Го катать, ёпта!',
    'Катка сама себя не скатает!',
    'Поиграем?',
]

TAG_COMMANDS = [
    '/ъ',
    '+',
    'ъ',
    'ауфпсы',
    'сбор',
    'милфысюда',
    'дедпоспел',
]

ALLOWED_CHATS = [
    1134285848,  # @voltovtom
    -1001787523639,  # КЛПД
]

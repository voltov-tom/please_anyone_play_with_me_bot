import random
import time
import telebot

from .hidden_settings import *
from asyncio import set_event_loop, new_event_loop
from telethon.sync import TelegramClient

TG_API_ID = API_ID
TG_API_HASH = API_HASH
TG_BOT_TOKEN = BOT_TOKEN
bot = telebot.TeleBot(TG_BOT_TOKEN)
bot_name = bot.get_me().username

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


@bot.message_handler(commands=['тест'])
def tag_all_participant(message):
    bot.send_message(message.chat.id, 'тест')


@bot.message_handler(commands=['ъ'])
def tag_all_participant(message):
    """
    :param message: triggered message to get all params
    :return: sent messages
    """
    from_user = message.from_user.username
    chat_id = message.chat.id
    all_users = get_all_chat_users(chat_id)
    all_users_count = len(all_users)
    limit = 5
    count = 0
    participants = ''

    for user in all_users:
        # пропускаем, если отправитель или бот
        if user.username == from_user or user.bot:
            count += 1
            continue

        # eсли нет username, тегаем по first_name
        if user.username is None and user.first_name:
            mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
            bot.send_message(
                message.chat.id, mention, parse_mode='HTML'
            )
            count += 1
            continue

        participant = '@' + user.username

        # специально для стаса и сережи
        if (from_user == 'stasucan' or from_user == 'gnu_brsk') and (
                participant == '@stasucan' or participant == '@gnu_brsk'):
            bot.send_message(
                message.chat.id, f'Эй пидр! {participant}'
            )
        else:
            participants += participant + ' '

        count += 1

        # отправляем пачкой по limit или то, что осталось
        if count % limit == 0 or count == all_users_count:
            message_part = random.choice(WAR_CRY)
            bot.send_message(
                message.chat.id, f'{message_part} {participants} '
            )
            participants = ''
            time.sleep(0.5)


def get_all_chat_users(chat_id):
    """
    :param chat_id: chat_id from triggered message
    :return: all_users
    """
    set_event_loop(new_event_loop())
    client = TelegramClient('bot', TG_API_ID, TG_API_HASH).start(bot_token=TG_BOT_TOKEN)
    client.connect()
    all_users = client.get_participants(chat_id)
    client.disconnect()
    return all_users


if __name__ == "__main__":
    try:
        bot.infinity_polling(interval=0, timeout=20, allowed_updates=['util.update_types'])
    except (KeyboardInterrupt, SystemExit):
        print("KeyboardInterrupt or exit(), goodbye!")
    except Exception as e:
        print(f"Uncaught exception: {e}")

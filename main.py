import telebot

from time import ctime, time, sleep
from asyncio import set_event_loop, new_event_loop
from telethon.sync import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN, TAG_COMMANDS, ALLOWED_CHATS
from parsing import get_random_gif_src

TG_API_ID = API_ID
TG_API_HASH = API_HASH
TG_BOT_TOKEN = BOT_TOKEN
bot = telebot.TeleBot(TG_BOT_TOKEN, threaded=False)
bot_name = bot.get_me().username


@bot.message_handler(content_types=['text'])
def entry_def(message):
    """
    :param message: messages handler to trigger definition
    :return:
    """
    chat_id = str(message.chat.id)
    if chat_id not in ALLOWED_CHATS:
        print(ctime(time()), chat_id)
        return

    msg = message.text.lower()

    if msg in ['gif', 'гиф']:
        get_gif(message)
    if msg in TAG_COMMANDS and good_night(message):
        tag_all_participant(message)
        sleep(300)
    if msg == '123':
        now = ctime(time())
        test(message, now)
        sleep(20)
# TODO добавить быструю ссылку на дискорд, быстрое отображение, кто в голосовом чате


# ограничение на ночь
def good_night(message):
    message_hour = ctime(message.date).split(' ')[4][:2]
    if int(message_hour) not in range(9, 23):
        bot.send_message(message.chat.id, 'Все уже спят...')
        return False
    else:
        return True


def test(message, now):
    bot.send_message(message.chat.id, now)


def get_gif(message):
    """
    :param message: triggered message to get all params
    :return: sent gif message or picture
    """
    chat_id = message.chat.id

    try:
        gif = open(get_random_gif_src(), 'rb')
        bot.send_animation(chat_id, gif)
        gif.close()
    except:
        bot.send_photo(message.chat.id, 'https://memepedia.ru/wp-content/uploads/2017/07/%D1%85%D0%BE%D1%85%D0%BE%D1%87%D1%83%D1%89%D0%B8%D0%B9-%D0%B8%D1%81%D0%BF%D0%B0%D0%BD%D0%B5%D1%86.jpg')
        bot.send_message(message.chat.id, 'еррор')


def tag_all_participant(message):
    """
    :param message: triggered message to get all params
    :return: sent messages
    """
    from_user = message.from_user.username
    all_users = get_all_chat_users(message.chat.id)
    all_users_count = len(all_users)
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

        # специально для mrRozhin
        if participant == '@mrRozhin':
            bot.send_message(
                message.chat.id, f'{participant}: "Сосать господин судья"'
            )
        # специально для стаса и сережи
        elif from_user == 'stasucan' and participant == '@gnu_brsk':
            bot.send_message(
                message.chat.id, f'Эй пидр! {participant} '
            )
        elif from_user == 'gnu_brsk' and participant == '@stasucan':
            bot.send_message(
                message.chat.id, f'Эй пидр! {participant} '
            )
        else:
            participants += participant + ' '

        count += 1

        # отправляем пачкой по limit или то, что осталось
        if (count % 5 == 0 and participants != '') or count == all_users_count:
            bot.send_message(
                message.chat.id, f'{participants} '
            )
            participants = ''


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

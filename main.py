import telebot

from time import ctime, time
from asyncio import set_event_loop, new_event_loop
from telethon.sync import TelegramClient

from parsing import get_random_gif_src
from config import API_ID, API_HASH, BOT_TOKEN, TAG_COMMANDS, ALLOWED_CHATS

TG_API_ID = API_ID
TG_API_HASH = API_HASH
TG_BOT_TOKEN = BOT_TOKEN
LAST_BOT_MSG = 0

bot = telebot.TeleBot(TG_BOT_TOKEN, threaded=False)


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
    if msg in TAG_COMMANDS and good_night(message) and time_diff(message):
        tag_all_participant(message)
    if msg == 'тест':
        test(message)


# отслеживание новых участников
@bot.message_handler(content_types=['new_chat_members'])
def handler_new_member(message):
    user_name = message.new_chat_members[0].first_name
    bot.send_message(message.chat.id, f'Ëктырмантыщко, {user_name}!')


# TODO добавить быструю ссылку на дискорд, быстрое отображение, кто в голосовом чате


# анти-спам
def time_diff(message):
    global LAST_BOT_MSG
    msg_time = int(message.date)
    if LAST_BOT_MSG == 0:
        LAST_BOT_MSG = msg_time
        return True
    else:
        if msg_time - LAST_BOT_MSG > 300:
            LAST_BOT_MSG = msg_time
            return True
        else:
            return False


# ограничение на ночь
def good_night(message):
    message_hour = ctime(message.date).split(' ')[4][:2]
    if int(message_hour) not in range(9, 22):
        bot.send_message(message.chat.id, 'Все уже спят...')
        return False
    else:
        return True


def test(message):
    from_user = message.from_user.username
    all_users = get_all_chat_users(message.chat.id)
    all_users_count = len(all_users)
    count = 0
    participants = []
    print(f'all_users_count={all_users_count}')

    for user in all_users:
        # пропускаем, если отправитель или бот
        if user.username == from_user or user.bot:
            count += 1
            continue

        # eсли нет username, тегаем по first_name
        if user.username is None and user.first_name:
            print(user.first_name)
            count += 1
            continue

        participant = '@' + user.username

        # специально для mrRozhin
        if participant == '@mrRozhin':
            print(
                f'{participant}: "Сосать господин судья"'
            )
            count += 1
        # специально для HomKaBrut
        elif participant == '@HomKaBrut':
            print(
                f'{participant}: "Вуф господин судья"'
            )
            count += 1
        # специально для стаса и сережи
        elif from_user == 'stasucan' and participant == '@gnu_brsk':
            print(
                f'Эй пидр! {participant} '
            )
            count += 1
        elif from_user == 'gnu_brsk' and participant == '@stasucan':
            print(
                f'Эй пидр! {participant} '
            )
            count += 1
        else:
            participants.append(participant)

    print(f'participants={participants}')
    message = ''

    for participant in participants:
        print(count)
        count += 1
        message += participant + ' '
        if count % 5 == 0 or count == all_users_count:
            print(message)
            message = ''
    return


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
    participants = []

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
            count += 1
        # специально для стаса и сережи
        elif from_user == 'stasucan' and participant == '@gnu_brsk':
            bot.send_message(
                message.chat.id, f'Эй пидр! {participant} '
            )
            count += 1
        elif from_user == 'gnu_brsk' and participant == '@stasucan':
            bot.send_message(
                message.chat.id, f'Эй пидр! {participant} '
            )
            count += 1
        else:
            participants.append(participant)

    tag_msg = ''
    for participant in participants:
        count += 1
        tag_msg += participant + ' '
        if count % 5 == 0 or count == all_users_count:
            bot.send_message(
                message.chat.id, f'{tag_msg} '
            )
            tag_msg = ''


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

import random
import telebot

from time import ctime, time, sleep
from asyncio import set_event_loop, new_event_loop
from telethon.sync import TelegramClient

from config import API_ID, API_HASH, BOT_TOKEN, WAR_CRY
from parsing import get_random_picture_src, get_random_gif_src

TG_API_ID = API_ID
TG_API_HASH = API_HASH
TG_BOT_TOKEN = BOT_TOKEN
bot = telebot.TeleBot(TG_BOT_TOKEN)
bot_name = bot.get_me().username


@bot.message_handler(commands=['тест'])
def tag_all_participant_test(message):
    chat_id = message.chat.id
    print('тест', ctime(time()))
    print('chat_id:', str(chat_id))
    if chat_id != -1001787523639:  # КЛПД
        return

    print(get_random_picture_src())
    print(get_random_gif_src())

    from_user = message.from_user.username
    all_users = get_all_chat_users(chat_id)
    all_users_count = len(all_users)
    group_users = 0
    count = 0
    participants = ''

    for user in all_users:
        print(count)
        print(user.username) if user.username else print(user.first_name)

        # пропускаем, если отправитель или бот
        if user.username == from_user or user.bot:
            count += 1
            print(from_user)
            continue

        # eсли нет username, тегаем по first_name
        if user.username is None and user.first_name:
            mention = f'Message: <a href="tg://user?id={user.id}">{user.first_name}</a>'
            count += 1
            print(mention)
            continue

        participant = '@' + user.username

        # специально для mrRozhin
        if participant == '@mrRozhin':
            print(f'Message: {participant}: "Сосать господин судья"')
        # специально для стаса и сережи
        elif from_user == 'stasucan' and participant == '@gnu_brsk':
            print(f'Message: Эй пидр! {participant} ')
        elif from_user == 'gnu_brsk' and participant == '@stasucan':
            print(f'Message: Эй пидр! {participant} ')
        else:
            participants += participant + ' '
            group_users += 1
            print(participants)
        count += 1

        # отправляем пачкой по 5 или то, что осталось
        if group_users % 5 == 0 or count == all_users_count:
            # message_part = random.choice(WAR_CRY)
            # bot.send_message(
            #     message.chat.id, f'{message_part} {participants} '
            # )
            print(f'Message: {participants}')
            participants = ''
            sleep(0.5)


@bot.message_handler(commands=['ъ'])
def tag_all_participant(message):
    """
    :param message: triggered message to get all params
    :return: sent messages
    """
    chat_id = message.chat.id
    print(ctime(time()), str(chat_id))
    if chat_id != -1001787523639:  # КЛПД
        return

    try:
        bot.send_video(message.chat.id, get_random_gif_src())
    except Exception:
        bot.send_photo(message.chat.id, 'https://memepedia.ru/wp-content/uploads/2017/07/%D1%85%D0%BE%D1%85%D0%BE%D1%87%D1%83%D1%89%D0%B8%D0%B9-%D0%B8%D1%81%D0%BF%D0%B0%D0%BD%D0%B5%D1%86.jpg')

    from_user = message.from_user.username
    all_users = get_all_chat_users(chat_id)
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

        # отправляем пачкой
        if count == all_users_count:
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

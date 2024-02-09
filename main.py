import telebot
import transliterate as transliterate

from time import ctime, time
from asyncio import set_event_loop, new_event_loop
from telebot import types
from telethon.sync import TelegramClient

from db_connector import create_db, check_user_in_chat, dont_tag_user_anywhere, check_user_status, \
    select_tags, select_games, select_users_for_game, add_new_game_name, add_game_tags_sql, select_all_users, \
    change_to_tag_list, get_players_sql
from parsing import get_random_gif_src
from config import API_ID, API_HASH, BOT_TOKEN, DEVELOPER_ID

TG_API_ID = API_ID
TG_API_HASH = API_HASH
TG_BOT_TOKEN = BOT_TOKEN
LAST_BOT_MSG = 0
TIMEOUT = 300  # таймаут между тэгами
USERS_FOR_NEW_GAME = []
NEW_GAME_NAME = ''

bot = telebot.TeleBot(TG_BOT_TOKEN, threaded=False)


# главная функция
@bot.message_handler(content_types=['text'])
def entry_def(message):
    msg = message.text.lower()

    if msg == '!' and str(message.from_user.id) == DEVELOPER_ID:
        all_users = get_all_chat_users(message.chat.id)
        create_db(all_users, bot)
        return

    chat_id = str(message.chat.id)

    if not check_user_in_chat(message, bot):
        bot.send_message(DEVELOPER_ID, f'Кто-то писал боту: {ctime(time())}, {chat_id}')
        return

    if msg == '/stop':
        return
    if msg == '/start':
        bot.send_message(message.chat.id, 'Я умею добавлять ключевые слова и тегать друзей(не обязательно друзей)')
        return
    if msg in ['gif', 'гиф']:
        get_gif(message)
        return
    # комент
    if msg == '/change_participation':
        change_participation(message)
        return
    if msg == '/dont_tag_me_anywhere':
        dont_tag_user(message)
        return
    if msg == '/status':
        get_user_status(message)
        return
    if msg == '/create_new_game':
        create_new_game_name(message)
        return
    if msg == '/change_tags':
        change_tags(message)
        return
    if msg == '/get_tags':
        get_game_name(message)
        return
    if msg == '/get_players':
        get_players(message)
        return

    # ищем тэг в сообщении
    for game in select_games():
        if msg in select_tags(game):
            if good_night(message) and time_diff(message):
                tag_participants(message, game)
                return


# изменить участие
def change_participation(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for game in select_games():
        games_keyboard = types.InlineKeyboardButton(text=game, callback_data="ch_part_" + game)
        keyboard.add(games_keyboard)

    stop_button = types.InlineKeyboardButton(text='---Скрыть меню---', callback_data='hide_')
    keyboard.add(stop_button)
    bot.send_message(message.chat.id, 'Где поменять?', reply_markup=keyboard)


# отключить все тэги для юзера
def dont_tag_user(message):
    sql_result = dont_tag_user_anywhere(message.from_user.id)
    if not sql_result:
        bot.send_message(message.from_user.id, 'Ошибка, попробуйте позже')
        return

    bot.send_message(message.from_user.id, 'Успех, все теги отключены')


# получить статус тэга юзера в игре
def get_user_status(message):
    status = dict(zip(select_games(), check_user_status(message)[0]))
    msg = ''
    for game_name in status:
        msg += f'{game_name}: вкл\n' if status.get(game_name) == 1 else f'{game_name}: выкл\n'

    bot.send_message(message.from_user.id, msg)


def create_new_game_name(message):
    send = bot.send_message(
        message.chat.id, 'Придумайте название игры или /stop'
    )

    bot.register_next_step_handler(send, convert_game_name)


# конвертация названия в латынь
def convert_game_name(message):
    if message.text == '/stop':
        return

    try:
        new_game_name = transliterate.translit(message.text, reversed=True)  # если есть кириллица -> латынь
    except transliterate.exceptions.LanguageDetectionError:  # исключение, если только латынь
        new_game_name = message.text

    new_game_name = ''.join(i for i in new_game_name if i.isalnum())  # чистим лишнее

    if not add_new_game_name(new_game_name):
        bot.send_message(message.chat.id, 'Название не может состоять только из цифр или такое название уже существует')
        return create_new_game_name(message)

    bot.register_next_step_handler(message, get_all_users, game_name=new_game_name)
    add_game_tag(message, new_game_name)


# список всех юзеров
def get_all_users(message, game_name):
    global NEW_GAME_NAME
    NEW_GAME_NAME = game_name

    keyboard = types.InlineKeyboardMarkup()
    for user in select_all_users():
        users_keyboard = types.InlineKeyboardButton(text=user[0], callback_data='add_usrs_' + str(user))
        keyboard.add(users_keyboard)

    stop_button = types.InlineKeyboardButton(text='---Стоп---', callback_data='stop_' + str(message.chat.id))
    keyboard.add(stop_button)
    bot.send_message(message.chat.id, 'Кого тегать в этой игре? Нажми стоп для остановки.', reply_markup=keyboard)


# изменить тэги для игры
def change_tags(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for game in select_games():
        games_keyboard = types.InlineKeyboardButton(text=game, callback_data='add_tags_' + game)
        keyboard.add(games_keyboard)

    stop_button = types.InlineKeyboardButton(text='---Скрыть меню---', callback_data='hide_')
    keyboard.add(stop_button)
    bot.send_message(message.chat.id, 'Где добавить?', reply_markup=keyboard)


# добавление тэгов
def add_game_tag(message, game_name):
    send = bot.send_message(
        message.chat.id, f'Придумайте тэги для {game_name}, через запятую, например: "флебофа, чебурек228, пылесосить" или /stop'
    )
    bot.register_next_step_handler(send, add_game_tags_sql, game_name, bot)


# получить имя игры от юзера
def get_game_name(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for game in select_games():
        games_keyboard = types.InlineKeyboardButton(text=game, callback_data='get_tags_' + game)
        keyboard.add(games_keyboard)

    stop_button = types.InlineKeyboardButton(text='---Скрыть меню---', callback_data='hide_')
    keyboard.add(stop_button)
    bot.send_message(message.chat.id, 'Где посмотреть?', reply_markup=keyboard)


# получить от юзера список новых тэгов
def get_tags(message, game_name):
    tags_list = select_tags(game_name)

    while None in tags_list:
        tags_list.remove(None)

    if tags_list:
        msg = '\n'.join(tags_list)
        bot.send_message(
            message.chat.id, f'Список тегов для {game_name}:\n{msg}'
        )
    else:
        bot.send_message(
            message.chat.id, f'Для {game_name} нет тэгов'
        )


# тэгнуть
def tag_participants(message, game):
    from_user_id = message.from_user.id
    for user in select_users_for_game(game):
        if user[0] == from_user_id:
            continue

        if user[1] == 'NULL':
            mention = f"<a href='tg://user?id={user[0]}'>{user[2]}</a>"
            bot.send_message(message.chat.id, mention, parse_mode='HTML')
            continue

        bot.send_message(message.chat.id, '@' + user[1])


# получить игроков для игры
def get_players(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for game in select_games():
        games_keyboard = types.InlineKeyboardButton(text=game, callback_data='get_players_' + game)
        keyboard.add(games_keyboard)

    stop_button = types.InlineKeyboardButton(text='---Скрыть меню---', callback_data='hide_')
    keyboard.add(stop_button)

    bot.send_message(message.chat.id, 'В какой игре посмотреть?', reply_markup=keyboard)


# TODO добавить быструю ссылку на дискорд, быстрое отображение, кто в голосовом чате


# анти-спам
def time_diff(message):
    global LAST_BOT_MSG
    msg_time = int(message.date)
    if LAST_BOT_MSG == 0:
        LAST_BOT_MSG = msg_time
        return True
    else:
        if msg_time - LAST_BOT_MSG > TIMEOUT:
            LAST_BOT_MSG = msg_time
            return True
        else:
            return False


# ограничение на ночь
def good_night(message):
    message_hour = ctime(message.date).split(' ')
    if '' in message_hour:
        message_hour.remove('')
    if int(message_hour[3][:2]) not in range(9, 23):
        bot.send_message(message.chat.id, 'Все уже спят...')
        return False
    else:
        return True


# рандомная гифка с joyreactor
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


# используя telegram api получить список юзеров в чате
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

# handlers ↓ ↓ ↓


# отслеживание новых участников
@bot.message_handler(content_types=['new_chat_members'])
def handler_new_member(message):
    # TODO добавить юзера в бд, как он вошел
    user_name = message.new_chat_members[0].first_name
    bot.send_message(message.chat.id, f'Ëктырмантыщко, {user_name}!')


# обработчик при изменении участия
@bot.callback_query_handler(func=lambda call: call.data.startswith('ch_part_'))
def callback_inline(call):
    call.data = call.data.replace("ch_part_", '')
    flag = change_to_tag_list(call.message.chat.id, call.data)

    if flag:
        bot.send_message(call.message.chat.id, f'{call.data}: вкл')
    else:
        bot.send_message(call.message.chat.id, f'{call.data}: выкл')


# обработчик при изменении тэгов
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_tags_'))
def callback_inline(call):
    call.data = call.data.replace('add_tags_', '')
    add_game_tag(call.message, call.data)
    bot.delete_message(call.message.chat.id, call.message.id)


# обработчик для получения тегов
@bot.callback_query_handler(func=lambda call: call.data.startswith('get_tags_'))
def callback_inline(call):
    call.data = call.data.replace('get_tags_', '')
    get_tags(call.message, call.data)
    bot.delete_message(call.message.chat.id, call.message.id)


# обработчик для списка юзеров для тега
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_usrs_'))
def callback_inline(call):
    global USERS_FOR_NEW_GAME

    user = call.data.replace('add_usrs_', '')
    chars = ["(", ")", "'"]
    for ch in user:
        if ch in chars:
            user = user.replace(ch, '')

    user = user.split(', ')
    USERS_FOR_NEW_GAME.append(user[1])
    bot.send_message(call.message.chat.id, user[0])


# обработчик для стопа выбора игроков
@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))
def callback_inline(call):
    global USERS_FOR_NEW_GAME, NEW_GAME_NAME
    if not NEW_GAME_NAME:
        return

    chat_id = call.data.replace('stop_', '')
    USERS_FOR_NEW_GAME = list(set(USERS_FOR_NEW_GAME))  # убираем дубли
    for user_id in USERS_FOR_NEW_GAME:
        change_to_tag_list(int(user_id), NEW_GAME_NAME)

    if USERS_FOR_NEW_GAME:
        bot.send_message(chat_id, f'Успех, ⇡⇡⇡ в {NEW_GAME_NAME}')
    else:
        bot.send_message(chat_id, f'Успех, но никто не выбран в {NEW_GAME_NAME}')
    bot.delete_message(chat_id, call.message.id)

    USERS_FOR_NEW_GAME = []
    NEW_GAME_NAME = ''


# обработчик для получения тегов
@bot.callback_query_handler(func=lambda call: call.data.startswith('get_players_'))
def callback_inline(call):
    call.data = call.data.replace('get_players_', '')
    bot.delete_message(call.message.chat.id, call.message.id)

    players = ''
    for user in get_players_sql(call.data):
        if user[1] == 'NULL':
            players += f'{user[2]}\n'
            continue
        players += f'@{user[1]}\n'

    bot.send_message(call.message.chat.id, f'Играют в {call.data}: \n{players}')


# обработчик для скрытия клавиатуры
@bot.callback_query_handler(func=lambda call: call.data.startswith('hide_'))
def callback_inline(call):
    bot.delete_message(call.message.chat.id, call.message.id)


if __name__ == "__main__":
    try:
        bot.infinity_polling(interval=0, timeout=20, allowed_updates=['util.update_types'])
    except (KeyboardInterrupt, SystemExit):
        print("KeyboardInterrupt or exit(), goodbye!")
    except Exception as e:
        print(f"Uncaught exception: {e}")

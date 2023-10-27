import os
import sqlite3

from config import DEVELOPER_ID

db_path = './PEPWMBOT'


def create_db(all_users, bot):
    if os.path.isfile(db_path):
        bot.send_message(DEVELOPER_ID, 'database exists')
        conn = sqlite3.connect(db_path)
        result = conn.execute('''SELECT * FROM users;''').fetchall()
        bot.send_message(DEVELOPER_ID, 'SELECT * FROM users;')

        if not result:
            bot.send_message(DEVELOPER_ID, 'база пуста')
            create_users_list(all_users, bot, conn)
        else:
            select = tuple()
            for res in result:
                select += str(res),
            bot.send_message(DEVELOPER_ID, ', '.join(select))
    else:
        bot.send_message(DEVELOPER_ID, 'database not exists')
        conn = sqlite3.connect('./PEPWMBOT')
        conn.execute('''
                        CREATE TABLE IF NOT EXISTS `users` (
                            [id] INTEGER PRIMARY KEY, [user_name] TEXT,
                            first_name TEXT DEFAULT (NULL),
                            valorant INTEGER DEFAULT (1), 
                            deep_rock INTEGER DEFAULT (0)
                        );
                    ''')
        conn.execute('''
                        CREATE TABLE IF NOT EXISTS `tag_commands` (
                            valorant TEXT DEFAULT (NULL),
                            deep_rock TEXT DEFAULT (NULL)
                        );
                    ''')
        conn.execute('''
                        INSERT INTO tag_commands (valorant, deep_rock) VALUES
                            ('/ъ', 'шахта'), 
                            ('ъ', 'копать'), 
                            ('ауфпсы', 'антижучес'), 
                            ('сбор', 'гномы'), 
                            ('милфысюда', NULL), 
                            ('дедпоспел', NULL),
                            ('просто плюс', NULL),
                            ('простоплюс', NULL),
                            ('я опорник', NULL),
                            ('псы войны', NULL),
                            ('го катку', NULL);
                    ''')
        create_users_list(all_users, bot, conn)

    conn.commit()
    conn.close()


def change_to_tag_list(user_id, game_name):
    conn = sqlite3.connect(db_path)
    flag = 1 - select_user_in_game(user_id, game_name)[0]  # swap 1 to 0, 0 to 1
    conn.execute(f'''
                    UPDATE users SET
                        {game_name} = {flag}
                    WHERE
                        id = '{user_id}';
                ''')
    conn.commit()
    conn.close()
    return flag


def select_user_in_game(user_id, game_name):
    conn = sqlite3.connect(db_path)
    result = conn.execute(
        f'''SELECT {game_name} FROM users WHERE id = {user_id};'''
    ).fetchone()
    conn.close()
    return result


def create_users_list(all_users, bot, conn):
    for user in all_users:
        if user.bot:
            continue
        if not user.username:
            user.username = 'NULL'
        if not user.first_name:
            user.first_name = 'NULL'

        bot.send_message(DEVELOPER_ID,
                         f'''
                               INSERT INTO users (id, user_name, first_name) VALUES 
                                   ('{user.id}', '{user.username}', '{user.first_name}')
                           ''')
        conn.execute(f'''
                               INSERT INTO users (id, user_name, first_name) VALUES 
                                   ('{user.id}', '{user.username}', '{user.first_name}')
                           ''')


def check_user_in_chat(message, bot):
    conn = sqlite3.connect(db_path)
    result = conn.execute(
                    f'''
                        SELECT * FROM users
                        WHERE id = {message.from_user.id};
                    ''').fetchall()
    if result:
        result = True
    else:
        bot.send_message(DEVELOPER_ID, f'Боту писал: {message.from_user}')
        result = False

    conn.close()
    return result


def dont_tag_user_anywhere(user_id):
    conn = sqlite3.connect(db_path)
    games_str = ''

    for game_name in select_games():
        games_str += f'{game_name} = 0, '
    games_str = games_str[:-2]  # remove the comma from the end

    result = conn.execute(
                    f'''
                        UPDATE users 
                        SET {games_str}
                        WHERE id = {user_id};
                    ''').rowcount
    if result:
        result = True
    else:
        result = False

    conn.commit()
    conn.close()
    return result


def check_user_status(message):
    conn = sqlite3.connect(db_path)

    games_str = ''
    for game_name in select_games():
        games_str += f'{game_name}, '
    games_str = games_str[:-2]  # remove the comma from the end

    result = conn.execute(
                    f'''
                        SELECT {games_str} FROM users
                        WHERE id = {message.from_user.id};
                    ''').fetchall()

    conn.close()
    return result


def select_tags(game_name):
    conn = sqlite3.connect(db_path)
    sql_result = conn.execute(f'''SELECT {game_name} FROM tag_commands;''').fetchall()

    result = []
    for i in sql_result:
        result.append(i[0])

    conn.close()
    return result


def select_games():
    conn = sqlite3.connect(db_path)
    sql_result = conn.execute(
        f'''
            PRAGMA TABLE_INFO('tag_commands');
        ''').fetchall()

    result = []
    for i in sql_result:
        result.append(i[1])

    conn.close()
    return result


def select_users_for_game(game_name):
    conn = sqlite3.connect(db_path)
    sql_result = conn.execute(f'''SELECT id, user_name, first_name FROM users WHERE {game_name} = 1;''').fetchall()
    conn.close()
    return sql_result


def add_new_game_name(game_name):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
                        f'''
                            ALTER TABLE users 
                            ADD {game_name} INTEGER DEFAULT (0)
                        ''')

        conn.execute(
                        f'''
                            ALTER TABLE tag_commands 
                            ADD {game_name} TEXT DEFAULT (NULL)
                        ''')

        conn.commit()
        conn.close()
        return True

    except sqlite3.OperationalError as error:
        print(error)
        conn.close()
        return False


def add_game_tags_sql(message, game_name, bot):
    if message.text == '/stop':
        return

    conn = sqlite3.connect(db_path)

    tags_arr = message.text.split(',')
    new_arr = []
    for el in tags_arr:
        new_arr.append(''.join(i for i in el if i.isalnum()).lower())  # чистим лишнее

    for tag in new_arr:
        if tag == '':
            new_arr.remove(tag)
            continue
        try:
            conn.execute(f'''INSERT INTO tag_commands ({game_name}) VALUES ('{tag}');''')
        except sqlite3.OperationalError as error:
            print(error)
            bot.send_message(message.chat.id, f'Произошла ошибка')
            conn.close()
            return False

    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f'Добавлены теги для {game_name}: {", ".join(new_arr)}')
    return True


def select_all_users():
    conn = sqlite3.connect(db_path)
    sql_result = conn.execute(f'''SELECT first_name, id FROM users;''').fetchall()
    conn.close()
    return sql_result

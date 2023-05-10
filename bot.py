import sqlite3
import logging
from turtledemo.penrose import start
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


conn = sqlite3.connect('passwords.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, chat_id INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS passwords
             (id INTEGER PRIMARY KEY, user_id INTEGER, service TEXT, login TEXT, password TEXT)''')
conn.commit()



def set_password(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if not result:
        c.execute("INSERT INTO users (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id))
        conn.commit()

    context.bot.send_message(chat_id=chat_id, text="Введите название сервиса:")
    context.user_data['next_step'] = 'login'
    context.user_data['service'] = update.message.text



def set_password_info(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    next_step = context.user_data.get('next_step')
    if next_step == 'login':
        context.user_data['next_step'] = 'password'
        context.user_data['login'] = update.message.text
        context.bot.send_message(chat_id=chat_id, text="Введите пароль:")
    elif next_step == 'password':
        service = context.user_data.get('service')
        login = context.user_data.get('login')
        password = update.message.text

        c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        result = c.fetchone()
        if result:
            user_id = result[0]
            c.execute("INSERT INTO passwords (user_id, service, login, password) VALUES (?, ?, ?, ?)",
                      (user_id, service, login, password))
            conn.commit()
            context.bot.send_message(chat_id=chat_id, text="Пароль успешно сохранен!")
        else:
            context.bot.send_message(chat_id=chat_id, text="Что-то пошло не так, попробуйте еще раз.")


def is_registered_user(chat_id):
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    result = c.fetchone()
    return bool(result)



def get_password(update, context):
    if not is_registered_user(update.message.chat_id):
        update.message.reply_text('Сначала зарегистрируйтесь с помощью команды /start')
        return

    if len(context.args) == 0:
        update.message.reply_text(
            'Укажите название сервиса, для которого нужно получить пароль, в формате: /get НАЗВАНИЕ_СЕРВИСА')
        return

    service_name = context.args[0]
    user_id = update.message.chat_id

    c.execute("SELECT password FROM passwords WHERE user_id=? AND service=?", (user_id, service_name))
    result = c.fetchone()
    if result:
        password = result[0]
        update.message.reply_text(f"Пароль для сервиса '{service_name}': {password}")
    else:
        update.message.reply_text(f"Пароль для сервиса '{service_name}' не найден")


database_file = "C:/Users/annar/PycharmProjects/bot_password/database.db"

conn = sqlite3.connect(database_file)
cursor = conn.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        service TEXT NOT NULL,
        login TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, service)
    )
""")


conn.commit()
conn.close()


def delete_password(update, context):
    if not is_registered_user(update.message.chat_id):
        update.message.reply_text('Сначала зарегистрируйтесь с помощью команды /start')
        return

    if len(context.args) == 0:
        update.message.reply_text(
            'Укажите название сервиса, который нужно удалить, в формате: /del НАЗВАНИЕ_СЕРВИСА')
        return

    service_name = context.args[0]

    c.execute('DELETE FROM passwords WHERE user_id=? AND service=?', (update.message.chat_id, service_name))
    conn.commit()



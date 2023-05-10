from turtledemo.forest import start
from telegram.ext import CommandHandler, Updater
from bot import set_password, get_password, delete_password

updater = Updater(token="6017736656:AAF_-6_1wR4FobGscAJHXG2kMGCnrVI2BNQ", use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('set', set_password))
dispatcher.add_handler(CommandHandler('get', get_password))
dispatcher.add_handler(CommandHandler('del', delete_password))


updater.start_polling()
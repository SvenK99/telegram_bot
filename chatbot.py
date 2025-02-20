from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
CallbackContext)
import configparser
import logging
import redis
global redis1
from telegram import Bot
from telegram.utils.request import Request
from HKBU_chatgpt import HKBU_ChatGPT

# # 在国内要设置代理，updater对象也要更新
# proxy1 = {
#     'proxy_url': 'http://127.0.0.1:10809',  # 代理地址
# }
#
# request = Request(proxy_url=proxy1['proxy_url'])
def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 在香港用这个updater
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)

    # #在国内用这个updater,python-telegram-bot 13.7 不能直接用updater来传入request需要经过Bot对象
    # ## 创建Bot对象时传入代理
    # bot = Bot(token=config['TELEGRAM']['ACCESS_TOKEN'], request=request)
    # ## 使用Bot对象来创建Updater对象
    # updater = Updater(bot=bot, use_context=True)

    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
    password=(config['REDIS']['PASSWORD']),
    port=(config['REDIS']['REDISPORT']),
    decode_responses=(config['REDIS']['DECODE_RESPONSE']),
    username=(config['REDIS']['USER_NAME']))
    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
    # # register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)
    # #dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),
                                     equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("delete", delete))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    # To start the bot:
    updater.start_polling()
    updater.idle()
def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
    # Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')
def hello(update: Update, context: CallbackContext) -> None:
    msg = context.args[0]
    update.message.reply_text('Good day, '+msg+'!')
def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' +
        redis1.get(msg) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
def delete(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        if redis1.get(msg):
            deleted_count=int(redis1.get(msg))
        else:
            deleted_count=0
        redis1.delete(msg)
        # print(deleted_count)
        if deleted_count>0 and deleted_count<=1 :
            update.message.reply_text('The keyword '+ msg +' has been deleted '+ str(deleted_count)+' time')
        elif deleted_count>1:
            update.message.reply_text('The keyword '+ msg +' has been deleted '+ str(deleted_count)+' times')
        else:
            update.message.reply_text('The keyword'+msg+'does not exist.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete <keyword>')



if __name__ == '__main__':
    main()

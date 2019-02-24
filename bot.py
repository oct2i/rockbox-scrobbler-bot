#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file contains that represents a Telegram Bot."""

import logging
import os
import re

import socks
import pylast

from datetime import datetime
from telegram import (KeyboardButton,
                      ReplyKeyboardMarkup,
                      ReplyKeyboardRemove,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup,
                      ParseMode)
from telegram.ext import (Updater,
                          Filters,
                          ConversationHandler,
                          CallbackQueryHandler,
                          CommandHandler,
                          MessageHandler)
import database
import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHANGE, LOGIN, PASSWORD = range(3)

def start(bot, update):
    text = ('Привет! Меня зовут *RockboxScrobblerBot*. Я буду помогать тебе '
            'с загрузкой журналов с Rockbox-плеера на сайт Last.fm.\n\nДля начала '
            'укажи свои данные используя команду /account.')
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def account(bot, update):
    user = update.message.from_user

    db = database.Connection()
    found, user_data = db.check_user(user.username)
    # found = False

    if found:
        text = 'Текущий аккаунт Last.fm:\n\n`{}`'.format(user_data['login'])
        keyboard_change = [
            [InlineKeyboardButton('Изменить аккаунт', callback_data='account_change')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard_change)
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

        return CHANGE

    else:
        text = ('Чтобы добавить акканут Last.fm, отправь мне логин и пароль. '
                'Не бойся, я не буду хранить твой пароль в открытом виде.')
        update.message.reply_text(text)
        text = 'Логин:'
        update.message.reply_text(text)

        db = database.Connection()
        db.add_user(user.username)

        return LOGIN

def account_change(bot, update):
    query = update.callback_query
    text = 'Хорошо. Отправь мне новый логин и пароль.'
    bot.send_message(text=text, chat_id=query.message.chat_id)
    text = 'Логин:'
    bot.send_message(text=text, chat_id=query.message.chat_id)

    return LOGIN

def account_login(bot, update):
    user = update.message.from_user
    login = update.message.text
    logger.info("%s %s" % (user.username, login))

    db = database.Connection()
    db.update_login(user.username, login)

    text = 'Пароль:'
    update.message.reply_text(text)

    return PASSWORD

def account_password(bot, update):
    user = update.message.from_user
    password = pylast.md5(update.message.text)

    logger.info("%s %s" % (user.username, password))

    db = database.Connection()
    db.update_password(user.username, password)

    text = ('Готово, теперь ты можешь загружать журналы! '
            'Для этого тебе нужно просто отправить мне файл.\n\n'
            'И да, для безопасности советую удалить сообщение с паролем из чата.')
    update.message.reply_text(text)

    return ConversationHandler.END


def upload(bot, update):
    user = update.message.from_user
    bot.send_message(text="Upload your log", chat_id=update.message.chat_id)
    scrob_log = bot.get_file(update.message.document.file_id)
    scrob_log.download('scrobbler.log')
    logger.info("user: %s\nfile_id:%s file_name:%s mime_type:%s file_size:%s", user.username,
                str(update.message.document.file_id), str(update.message.document.file_name),
                str(update.message.document.mime_type), str(update.message.document.file_size))
    exit(0)

    bot.send_message(text="Done. Open log", chat_id=update.message.chat_id)
    plays = []
    try:
        with open(config.LASTFM_LOG_LOCATION, 'r') as f:
            plays = f.readlines()
    except KeyError:
        logger.info("Error:" + config.LASTFM_LOG_LOCATION + "env var not set")
    except IOError:
        logger.info("Error: Log file not found")

    plays = plays[3:]
    logger.info(plays)

    lastfm_username = 'scrobbler_test'
    lastfm_password = pylast.md5("jEOY\E9o4x")
    lastfm_network = pylast.LastFMNetwork(api_key=config.API_KEY, api_secret=config.API_SECRET,
                                          username=lastfm_username, password_hash=lastfm_password)

    for line in plays:
        line = re.split(r'\t+', line)
        if (line[5] == "L"):
            #logger.info("Scrobbling: " + line[0]  + " - " + line[2])
            #logger.info(line[0], line[2], line[6])
            print(line[0], line[2], line[6])
            exit(1)
            lastfm_network.scrobble(artist=line[0], title=line[2], timestamp=line[6])
        else:
            print("Skipped: " + line[0] + " - " + line[2])


def edit():
    pass

def share(bot, update):
    message = 'Загрузи свой журнал на Last.fm!\n'
    keyboard_share = [
        [InlineKeyboardButton('Поделиться', switch_inline_query=message)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_share)
    text = 'Делись ссылкой с Rockbox-друзьями!'
    update.message.reply_text(text, reply_markup=reply_markup)

def help(bot, update):
    space = '\u0020'
    text = ('*Список команд*:\n'
            '/start{0}старт\n'
            '/account{1}данные Last.fm\n'
            '/share{2}рассказать друзьям\n'
            '/help{3}помощь\n\n'
            'Для загрузки журнала просто отправь мне файл.\n\n'
            'С вопросом или предложением обращайся к @oct2i.'.format(space*8, space*2, space*6, space*8))
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def unknown(bot, update):
    text = 'Увы, я не знаю такой команды.'
    update.message.reply_text(text)

def error(update, error):
    text = 'Update "{}" caused error "{}"'.format(update, error)
    logger.warning(text)

def main():
    # Create the Updater and pass it bot's token
    updater = Updater(token=config.BOT_TOKEN, request_kwargs=config.REQUEST_KWARGS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add authentication handler with the states
    account_handler = ConversationHandler(
        entry_points=[CommandHandler("account", account)],
        states={
            CHANGE: [CallbackQueryHandler(account_change)],
            LOGIN: [MessageHandler(Filters.text, account_login)],
            PASSWORD: [MessageHandler(Filters.text, account_password)]
        },
        fallbacks=[CommandHandler('account', account)]
    )

    # Add command handlers
    dp.add_handler(account_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("edit", edit))
    dp.add_handler(CommandHandler("share", share))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.document, upload))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully
    updater.idle()

if __name__ == '__main__':
    main()

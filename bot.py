#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file contains that represents a Telegram Bot."""

import os
import re
import logging
from datetime import datetime

import socks
import pylast
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


# Enable logging in file
logging.basicConfig(filename=config.LOGGER_FILE,
                    filemode='a',
                    format='%(asctime)s - %(name)-4s - %(levelname)-7s - %(filename)s:%(lineno)d - %(message)s',
                    level=logging.WARNING)

logger = logging.getLogger('bot')

# The states account handler
CHANGE, LOGIN, PASSWORD = range(3)


def start(bot, update):
    text = ('Привет! Меня зовут *RockboxScrobblerBot*. Я буду помогать тебе '
            'с загрузкой журналов с Rockbox-плеера на сайт Last.fm.\n\n'
            'Для начала укажи свои данные используя команду /account.')
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


def account(bot, update):
    user = update.message.from_user

    db = database.Connection()
    found, user_data = db.check_user(user.username)

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

    db = database.Connection()
    db.update_login(user.username, login)

    text = 'Пароль:'
    update.message.reply_text(text)

    return PASSWORD


def account_password(bot, update):
    user = update.message.from_user
    password = pylast.md5(update.message.text)

    db = database.Connection()
    db.update_password(user.username, password)

    text = ('Готово, теперь ты можешь загружать журналы! '
            'Для этого тебе нужно просто отправить мне файл.\n\n'
            'И да, для безопасности советую удалить сообщение с паролем из чата.')
    update.message.reply_text(text)

    return ConversationHandler.END


def upload(bot, update):
    user = update.message.from_user

    db = database.Connection()
    found, user_data = db.check_user(user.username)

    if found:
        if user_data['login'] and user_data['password']:
            log_id = update.message.document.file_id
            log_name = update.message.document.file_name
            log_size = update.message.document.file_size
            log_mime_type = update.message.document.mime_type
            log_user_dir = '{}/{}'.format(config.LOG_DIR, user.username)
            log_path = '{}/scrobbler.log'.format(log_user_dir)
            log_more = ('More about log file: {} | {} byte | {} | '
                        '{}.'.format(log_name, log_size, log_mime_type, log_user_dir))

            if log_mime_type == 'text/x-log':
                if log_size < config.LOG_SIZE_MAX:

                    if not os.path.exists(log_user_dir):
                        os.makedirs(log_user_dir)

                    log_file = bot.get_file(log_id)
                    log_file.download(log_path)

                    text = 'Обрабатывается журнал: *{}*'.format(log_name)
                    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

                    success, report = processing(log_path, user_data)

                    if success:
                        db = database.Connection()
                        db.update_upload_date(user.username, str(datetime.now()))
                        text = ('Готово! Заскробблено треков: *{}*.\n\nНе забудь удалить '
                                'исходный журнал с плеера, он больше не нужен.'.format(report['track']))
                        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                    else:
                        if report['error'] == 'account':
                            text = ('Ошибка в *данных аккаунта Lastfm*! Для редактирования '
                                    'используй команду /account, а потом попробуй снова.')
                            update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                        elif report['error'] == 'read':
                            text = 'Не могу прочитать *журнал*! Проверь его, а потом попробуй снова.'
                            update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                            logger.error(log_more)
                        else:
                            text = '*Что-то* пошло не так! Попробуй снова.'
                            update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                            logger.error(log_more)

                else:
                    text = ('Ого, какой *большой журнал*! Извини, но я не работаю с журналами '
                            'таких размеров. Разбей его на части поменьше и попробуй снова.')
                    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                    text = ('Log file larger than 2Mb. {}'.format(log_more))
                    logger.warning(text)
            else:
                text = 'Не могу понять, это *журнал или нет*?! Попробуй снова.'
                update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                text = ('File extension is not ".log". {}'.format(log_more))
                logger.warning(text)

        else:
            text = 'Ты не указал(а) данные аккаунта Last.fm, для этого используй команду /account.'
            update.message.reply_text(text)
    else:
        text = 'Ты не указал(а) данные Last.fm, для этого используй команду /account.'
        update.message.reply_text(text)


def processing(log_path, user_data):
    # Format header lines indicated by the leading '#' character:
    # - #AUDIOSCROBBLER/1.1
    # - #TZ/[UNKNOWN|UTC]
    # - #CLIENT/<IDENTIFICATION STRING>
    #
    # Format track comprise fields and separated are tab (\t):
    # - artist name
    # - album name (optional)
    # - track name
    # - track position on album (optional)
    # - song duration in seconds
    # - rating (L if listened at least 50% or S if skipped)
    # - unix timestamp when song started playing
    # - MusicBrainz Track ID (optional)
    success = False
    report = {
        'error': None,
        'track': 0
    }

    try:
        # Reading log file
        with open(log_path, 'r') as f:
            tracks = f.readlines()
        # Connection to Last.fm
        network = pylast.LastFMNetwork(api_key=config.API_KEY,
                                       api_secret=config.API_SECRET,
                                       username=user_data['login'],
                                       password_hash=user_data['password'])
        # Parsing and scrobbling data
        for track in tracks:
            if track[0] != '#':
                field = re.split(r'\t+', track)
                if field[5] == 'L':
                    network.scrobble(artist=field[0], title=field[2], timestamp=field[6])
                    report['track'] += 1
        # Status
        success = True
    except KeyError:
        logger.error('Not found log directory "{}"'.format(log_path))
    except IOError:
        logger.error('Not found log file "{}"'.format(log_path))
    except UnicodeDecodeError:
        logger.error('Read error log file "{}"'.format(log_path))
        report['error'] = 'read'
    except pylast.WSError:
        logger.error('Authentication error from user "{}"'.format(user_data['username']))
        report['error'] = 'account'
    except Exception as e:
        logger.error('Unknown error "{}" log file "{}"'.format(e, log_path))
        report['error'] = 'unknown'
    finally:
        return success, report


def share(bot, update):
    message = 'Загрузи свой журнал на Last.fm!'
    keyboard_share = [
        [InlineKeyboardButton('Поделиться', switch_inline_query=message)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_share)
    text = 'Делись ссылкой с Rockbox-друзьями!'
    update.message.reply_text(text, reply_markup=reply_markup)


def help(bot, update):
    text = ('Список команд:\n'
            '/start{0}старт\n'
            '/account{1}данные Last.fm\n'
            '/share{2}рассказать друзьям\n'
            '/help{0}помощь\n\n'
            'Для загрузки журнала просто отправь мне файл.\n\n'
            'С вопросом или предложением обращайся к @oct2i.'.format(' '*8, ' '*2, ' '*6))
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

    # Add account handler with the states
    account_handler = ConversationHandler(
        entry_points=[CommandHandler('account', account)],
        states={
            CHANGE: [CallbackQueryHandler(account_change)],
            LOGIN: [MessageHandler(Filters.text, account_login)],
            PASSWORD: [MessageHandler(Filters.text, account_password)]
        },
        fallbacks=[CommandHandler('account', account)]
    )

    # Add command handlers
    dp.add_handler(account_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('share', share))
    dp.add_handler(CommandHandler('help', help))
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

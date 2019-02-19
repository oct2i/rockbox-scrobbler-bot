#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file contains that represents a Telegram Bot."""

import logging
import telegram
import socks
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
import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    bot.send_message(text="Hi",
                     chat_id=update.message.chat_id)

def unknown(bot, update):
    bot.send_message(text="Oops", chat_id=update.message.chat_id)

def error(bot, update, error):
    text = 'Update "{}" caused error "{}"'.format(update, error)
    logger.warning(text)

def main():
    # Create the Updater and pass it bot's token
    updater = Updater(config.bot_token, request_kwargs=config.REQUEST_KWARGS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Answers on different commands
    dp.add_handler(CommandHandler("start", start))

    # Answer on noncommand
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

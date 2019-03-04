# -*- coding: utf-8 -*-
"""This file contains configuration the Telegram Bot."""

BOT_TOKEN = 'token'

# Settings proxy
REQUEST_KWARGS = {
    'proxy_url': 'socks5://ip',
    'urllib3_proxy_kwargs': {
        'username': 'login',
        'password': 'pass',
    }
}

# Settings logger
LOGGER_FILE = 'logs/bot.log'

# Settings database
DATABASE_HOST = 'host'
DATABASE_USER = 'login'
DATABASE_PASSWORD = 'pass'
DATABASE_NAME = 'name'

# Settings Last.fm account
API_KEY = 'key'
API_SECRET = 'secret'

# Settings scrobbler log file
LOG_DIR = 'logs'
LOG_SIZE_MAX = (1024*1024)*2  # 2Mb

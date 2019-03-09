# -*- coding: utf-8 -*-
"""This file contains configuration the Telegram Bot."""

BOT_TOKEN = 'your-token'

# Settings proxy (if Telegram is not available from you)
REQUEST_KWARGS = {
    'proxy_url': 'socks5://your-ip:port',
    'urllib3_proxy_kwargs': {
        'username': 'your-login',
        'password': 'your-pass',
    }
}

# Settings logger
LOGGER_FILE = 'logs/bot.log'

# Settings database
DATABASE_HOST = 'your-host'
DATABASE_USER = 'your-login'
DATABASE_PASSWORD = 'your-pass'
DATABASE_NAME = 'your-name'

# Settings Last.fm account
API_KEY = 'your-key'
API_SECRET = 'your-secret'

# Settings scrobbler log file
LOG_DIR = 'logs'
LOG_SIZE_MAX = (1024*1024)*2  # 2Mb

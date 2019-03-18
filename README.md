# RockboxScrobblerBot

Telegram bot for scrobbling logs at **Last.fm** from portable music players working with **Rockbox** firmware.

Features:
* can not edit the log via the bot
* size max log 2Mb

Upload your log on the **Last.fm**! [Try it now](https://t.me/RockboxScrobblerBot).


## Backend

Bot written in Python, used [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework, [pylast](https://github.com/pylast/pylast) interface to Last.fm and [PyMySQL](https://github.com/PyMySQL/PyMySQL) library for database contact.

Developed in the following environment:
* `Python 3.5.2`
* `MySQL 5.7.25`
* `Pip latest version`

Python dependencies:
* `python-telegram-bot==11.1.0`
* `pylast==3.0.0`
* `PyMySQL==0.9.3`

Rest of the python dependencies see in the file [requirements.txt](requirements.txt).

Also note the file [config.py](config.py).


## References

* [Telegram bots](https://core.telegram.org/bots)
* [Rockbox firmware](https://www.rockbox.org/)
* [Last.fm API](https://www.last.fm/api/intro)


## License

This software is licensed under the terms of the GNU General Public License version 3.

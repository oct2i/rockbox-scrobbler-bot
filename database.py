# -*- coding: utf-8 -*-
"""This file contains work of the Telegram Bot with database."""

import pymysql.cursors
import config


class Connection:

    def __init__(self):
        """Connect to the database"""
        self.connection = pymysql.connect(host=config.DATABASE_HOST,
                                          user=config.DATABASE_USER,
                                          password=config.DATABASE_PASSWORD,
                                          db=config.DATABASE_NAME,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def check_user(self, username):
        """User search in the database"""
        try:
            with self.connection.cursor() as cursor:
                select = ('SELECT `username`, \
                                  `login`, \
                                  `password`, \
                                  `last_upload` \
                           FROM `users` WHERE `username`=%s')
                cursor.execute(select, (username,))
                user_data = cursor.fetchone()
                found = False if user_data is None else True
                return found, user_data
        finally:
            self.connection.close()

    def add_user(self, username):
        """Adding a user to the database"""
        try:
            with self.connection.cursor() as cursor:
                insert = 'INSERT INTO `users` (`username`) VALUES (%s)'
                cursor.execute(insert, (username,))
                self.connection.commit()
        finally:
            self.connection.close()

    def update_login(self, username, login):
        """Login update in the database"""
        try:
            with self.connection.cursor() as cursor:
                update = 'UPDATE `users` SET `login`=%s WHERE `username`=%s'
                cursor.execute(update, (login, username,))
                self.connection.commit()
        finally:
            self.connection.close()

    def update_password(self, username, password):
        """Password update in the database"""
        try:
            with self.connection.cursor() as cursor:
                update = 'UPDATE `users` SET `password`=%s WHERE `username`=%s'
                cursor.execute(update, (password, username,))
                self.connection.commit()
        finally:
            self.connection.close()

    def update_upload_date(self, username, last_upload):
        """Update the last upload date in the database"""
        try:
            with self.connection.cursor() as cursor:
                update = 'UPDATE `users` SET `last_upload`=%s WHERE `username`=%s'
                cursor.execute(update, (last_upload, username,))
                self.connection.commit()
        finally:
            self.connection.close()

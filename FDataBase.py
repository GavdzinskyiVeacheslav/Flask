import math
import re
import sqlite3
import time

from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Error reading from DB")
        return []

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(
                f"SELECT COUNT() as `count` FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("An article with this url already exists")
                return False

            base = url_for('static', filename='images_html')

            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = math.floor(time.time())
            self.__cur.execute(
                'INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)', (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error adding article to DB"+str(e))
            return False

        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(
                f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Error getting article from DB "+str(e))

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(
                f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Error getting article from DB "+str(e))

        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("User with this email already exists")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error adding user to DB "+str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f'SELECT * FROM users WHERE id = {user_id} LIMIT 1')
            res = self.__cur.fetchone()
            if not res:
                print('User not found')
                return False

            return res
        except sqlite3.Error as e:
            print("Error adding user to DB "+str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f'SELECT * FROM users WHERE email = "{email}" LIMIT 1')
            res = self.__cur.fetchone()
            if not res:
                print("User not found")
                return False

            return res
        except sqlite3.Error as e:
            print("Error adding user to DB " + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f'UPDATE users SET avatar = ? WHERE id = ?', (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print('DB avatar update error: ' +str(e))
            return False
        return True
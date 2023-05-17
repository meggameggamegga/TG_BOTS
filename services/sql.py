import sqlite3
from datetime import datetime


class DataBase:
    def __init__(self,db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    #Проверка есть ли пользователь в базе данных (users)
    async def user_exist(self,user_id):
        with self.connect:
            data = self.cursor.execute('''SELECT * FROM users WHERE user_id=(?)''',
                                       [user_id]).fetchall()
        return bool(len(data))#True 1 False 0

    #Добавление пользователя в БД (users)
    async def add_user(self,user_id,name=None):
        with self.connect:
            if name:
                data = self.cursor.execute('''INSERT INTO users(user_id,name) VALUES (?,?)''',
                                           [user_id,name])
            else:
                data = self.cursor.execute('''INSERT INTO users(user_id) VALUES (?)''',
                                           [user_id])
        return data


    #Добавление задачи (notification)
    async def add_new_task(self,user_id,alert,time):
        with self.connect:
            return self.cursor.execute('''INSERT INTO notification(user_id,alert,time) VALUES(?,?,?)''',
                                       [user_id,alert,time])


    #Вытаскиваем все задачи пользователя (notification)
    async def get_all_notify(self,user_id):
        with self.connect:
            data = self.cursor.execute('''SELECT alert,time FROM notification WHERE user_id=(?)''',
                                       [user_id]).fetchall()
        return data if data else None

    #Вытаскиваем все задачи и user_id по истечению времени
    async def get_all_user_alert(self):
        with self.connect:
            data = self.cursor.execute('''SELECT user_id, alert FROM notification WHERE time <=(?)''',
                                       [datetime.now()]).fetchall()
        try:
            if data[0][1] != None:
                return data
        except Exception as e:
            return None


    #Удаление всех задач
    async def del_task_user(self,user_id):
        with self.connect:
            return self.cursor.execute('''DELETE FROM notification WHERE user_id=(?)''',
                                       [user_id])

    #Удаление конктретной задачи
    async def del_task(self,alert):
        with self.connect:
            return self.cursor.execute('''DELETE FROM notification WHERE alert=(?)''',
                                       [alert])

    #Изменение времени
    async def change_time(self,time,user_id,task):
        with self.connect:
            return self.cursor.execute('''UPDATE notification SET time=(?) WHERE user_id=(?) AND alert=(?)''',
                                       [time,user_id,task])

    #Изменение задачи
    async def change_alert(self,alert,user_id,time):
        with self.connect:
            return self.cursor.execute('''UPDATE notification SET alert=(?) WHERE user_id=(?) AND time=(?)''',
                                       [alert,user_id,time])
    #Получение времени
    async def get_time(self,user_id,alert):
        with self.connect:
            data = self.cursor.execute('''SELECT time FROM notification WHERE user_id=(?) AND alert=(?)''',
                                       [user_id,alert]).fetchone()
        return data[0]
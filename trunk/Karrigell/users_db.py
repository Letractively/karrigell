import os
import sqlite3
import hashlib

levels = {'admin':1000,'edit':500,'visit':100}

class SQLiteUsersDb:

    def __init__(self,path):
        self.path = path
        if not os.path.exists(path):
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE users (login TEXT,password TEXT,\
                role TEXT, skey TEXT)')
            cursor.execute('CREATE TABLE folders (folder_url TEXT, level TEXT,\
                login_url TEXT)')
            conn.commit()
            conn.close()
            conn = sqlite3.connect(path)
            cursor = conn.cursor()

    def is_empty(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT login FROM users')
        return not bool(cursor.fetchall())

    def is_valid(self,cookies,role):
        if not role in levels:
            raise ValueError('Unknow role : {} - must be one of {}'.format(
                role,list(levels.keys())))
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        if not 'login' in cookies or not 'skey' in cookies:
            return False
        login = cookies['login'].value
        skey = cookies['skey'].value
        cursor.execute('SELECT role FROM users WHERE login=? AND skey=?',
            (login,skey))
        result = cursor.fetchall()
        if not result:
            return False
        else:
            _role = result[0][0]
            return levels[_role] >= levels[role]

    def role(self,login,password):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        _hash = hashlib.md5()
        _hash.update(password.encode('utf-8'))
        cursor.execute('SELECT role FROM users WHERE login=? AND password=?',
            (login,_hash.digest()))
        results = cursor.fetchall()
        if not results:
            return None
        else:
            return results[0][0]

    def set_session_key(self,login,skey):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET skey=? WHERE login=?',(skey,login))
        conn.commit()

    def set_admin(self,login,password):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        _hash = hashlib.md5()
        _hash.update(password.encode('utf-8'))
        cursor.execute('INSERT INTO users (login,password,role) \
            VALUES (?,?,?)',(login,_hash.digest(),'admin'))
        conn.commit()

    def infos(self,folder_url):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT level,login_url FROM folders WHERE folder_url=?',(folder_url,))
        result = cursor.fetchall()
        if not result:
            return 'All',''
        else:
            return result[0]

    def set_folder_level(self,folder_url,level,login_url):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT level FROM folders WHERE folder_url=?',(folder_url,))
        result = cursor.fetchall()
        if not result:
            cursor.execute('INSERT INTO folders (folder_url,level,login_url) \
                VALUES(?,?,?)',(folder_url,level,login_url))
        else:
            cursor.execute('UPDATE folders SET level=?,login_url=? WHERE folder_url=?',
                (level,login_url,folder_url))
        conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.path)
    
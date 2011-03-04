import os
import sqlite3
import hashlib

levels = {'admin':1000,'edit':500,'visit':100}

class SQLiteUsersDb:

    def __init__(self,path):
        self.path = path
        self.name = path
        if not os.path.exists(path):
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE users (login TEXT,password TEXT,\
                role TEXT, skey TEXT)')
            conn.commit()
            conn.close()

    def is_empty(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT login FROM users')
        return not bool(cursor.fetchall())

    def key_has_role(self,skey,req_role):
        """Test if the database has a user with the session key "skey" 
        and if so, if its role is greater or equal to req_role"""
        if not req_role in levels:
            fmt = 'Unknow role : {} - must be one of {}'
            raise ValueError(fmt.format(req_role,list(levels.keys())))
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE skey=?',(skey,))
        result = cursor.fetchall()
        if not result:
            return False
        else:
            return levels[result[0][0]] >= levels[req_role]

    def user_has_role(self,login,password,req_role):
        """Test if the database has a user with the specified login
        and password and if so, if its role is greater or equal to req_role"""
        if not req_role in levels:
            fmt = 'Unknow role : {} - must be one of {}'
            raise ValueError(fmt.format(req_role,list(levels.keys())))
        role = self.role(login,password)
        if role is None:
            return False
        return levels[role] >= levels[req_role]

    def get_role(self,skey):
        """Return the role of user with session key skey"""
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE skey=?',(skey,))
        result = cursor.fetchall()
        if not result:
            return None
        else:
            return result[0][0]

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

    def get_connection(self):
        return sqlite3.connect(self.path)

class SQLiteTranslationDb:

    def __init__(self,path):
        self.path = path
        if not os.path.exists(path):
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE translation_original (original TEXT)')
            cursor.execute('CREATE TABLE translation (orig_id INTEGER, \
                language TEXT, translated TEXT)')
            conn.commit()
            conn.close()

    def get_translation(self,src,language):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT rowid FROM translation_original '
            'WHERE original = ?',(src,))
        result = cursor.fetchall()
        if not result:
            return None
        else:
            rowid = result[0][0]
            cursor.execute('SELECT translated FROM translation '
                'WHERE orig_id=? AND language=?',(rowid,language))
            result = cursor.fetchall()
            if not result:
                return None
            else:
                return result[0][0]

    def set_translation(self,src,language,translated):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT rowid FROM translation_original '
            'WHERE original = ?',(src,))
        result = cursor.fetchall()
        if not result:
            cursor.execute('INSERT INTO translation_original '
                '(original) VALUES (?)',(src,))
            rowid = cursor.lastrowid
            conn.commit()
        else:
            rowid = result[0][0]
        cursor.execute('SELECT translated FROM translation '
            'WHERE orig_id=? AND language=?',(rowid,language))
        result = cursor.fetchall()
        if not result:
            cursor.execute('INSERT INTO translation '
                '(orig_id,language,translated) VALUES (?,?,?)',
                (rowid,language,translated))
            conn.commit()
        elif translated != result[0][0]:
            cursor.execute('UPDATE translation '
                'SET translated=? WHERE orig_id=? AND language=?',
                (translated,rowid,language))
            conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.path)
        
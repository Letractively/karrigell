import Karrigell
import Karrigell.admin_db

class App(Karrigell.App):
    root_dir = r'c:\Karrigell-Python3\tests'
    users_db = Karrigell.admin_db.SQLiteUsersDb(r'c:\Karrigell-Python3\admin_tools\users.sqlite')
    login_url = '/admin/login.py/login'

class AdminApp(Karrigell.App):
    root_url = '/admin'
    root_dir = r'c:\Karrigell-Python3\20110307\admin_tools'

apps = [App(),AdminApp()]

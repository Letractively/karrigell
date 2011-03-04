# -*- coding: latin-1 -*-

import sys
k_path = r'c:\Karrigell-Python3\20110223_2'
sys.path.insert(0,k_path)

import Karrigell
import Karrigell.admin_db

def forbid_extensions(handler):
    for ext in ['.sqlite']:
        if handler.path.endswith(ext):
            raise Karrigell.HTTP_ERROR(403)

class App1(Karrigell.App):
    
    users_db = Karrigell.admin_db.SQLiteUsersDb('users.sqlite')
    translation_db = Karrigell.admin_db.SQLiteTranslationDb('translations.sqlite')

    protected = ['test']
    def limit_to_admin(handler):
        # limit access to protected folders to admins
        if handler.path.split('/')[1] in protected \
            and not handler.role('admin'):
                raise Karrigell.HTTP_REDIRECTION('/login.py/login')

    def smart_urls(handler):
        # redirect urls like host/script.py/func/foo/bar to
        # host/script.py/func?foo=&bar=
        elts = handler.path_info.split('/')
        for i,elt in enumerate(elts):
            if elt.endswith('.py') and len(elts)>i+2:
                smart_args = "&".join("{}=".format(elt) for elt in elts[i+2:])
                redir_to = '/'.join(elts[:i+2])+'?'+smart_args
                raise Karrigell.HTTP_REDIRECTION(redir_to)

    filters = [forbid_extensions]

class App2(Karrigell.App):

    root_url = '/test'
    root_dir = r'c:\Karrigell-Python3\héhé'
    login_url = '/test/admin_tools/login.py/login'
    users_db = Karrigell.admin_db.SQLiteUsersDb(r'c:\temp\users_db.sqlite')

Karrigell.run(apps=[App1(),App2()])

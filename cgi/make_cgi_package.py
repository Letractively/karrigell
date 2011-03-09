import os
import shutil
import datetime

import Karrigell

name = 'Karrigell-{}-cgi'.format(Karrigell.version)
parent = os.path.dirname(os.getcwd())

dest_dir = os.path.join(os.getcwd(),'cgi-package')
if os.path.exists(dest_dir):
    shutil.rmtree(dest_dir)
os.mkdir(dest_dir)
local_cgi_dir = os.path.join(dest_dir,'cgi_directory')
os.mkdir(local_cgi_dir)
local_root_dir = os.path.join(dest_dir,'root_directory')
os.mkdir(local_root_dir)

print(
"""Builds a Karrigell package to install in the CGI folder of a web server

The package will be in the subfolder "cgi-package" of this folder.

The CGI handler needs to know the path of the Python interpreter. If the 
package is going to be used on a different machine, for instance on a shared 
web hosting, enter the path on this machine

It is usually something like "c:/Python3.x/python.exe" or simply "python" on 
Windows, and /usr/local/bin/python on Unix-like operating systems. If you are 
not sure, ask the administrator or check the site documentation
""")
python_path = input('Python interpreter path : ')

print("""
You must define at least 1 application, served by the "root url", for instance
"/" if the applications serves the server document root, or "/foo" if the
application serves the requests at addresses like 
http://host/foo/script.py/func""")

while True:
    root_url = input('Root url (must begin with /) : ')
    if root_url.startswith('/'):
        break

print("""
Specify the directory in the file system where the scripts for this root url
are found""")

while True:
    root_dir = input('Root directory : ')
    if root_dir:
        break

while True:
    set_users_db = input("Do you want to set up a users database (Y/N) ? ")
    if set_users_db.lower() in "yn":
        break

if set_users_db.lower()=="y":
    print("Users data will be stored in a SQLite database. You must specify "
    "the path in the file system for this database. Make sure not to put it "
    "in the root directory defined above, for security reasons")
    while True:
        users_db_path = input("Path of SQLite database in the file system : ")
        if users_db_path:
            break

out = open(os.path.join(local_cgi_dir,'cgi_config.py'),'w')
out.write("# generated ")
out.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n"))
out.write("""import Karrigell
import Karrigell.admin_db

class App(Karrigell.App):
    root_url = '{}'
    root_dir = r'{}'""".format(root_url,root_dir))

if set_users_db.lower() == "y":
    out.write("\n    users_db = Karrigell.admin_db.SQLiteUsersDb(r'{}')".format(
        users_db_path))
    login_url = root_url.rstrip('/')+'/admin/login.py/login'
    out.write("\n    login_url = '{}'".format(login_url))

out.write('\n\napps = [App()]\n')

# create folder for document root with the .htaccess file and an index file
while True:
    cgi_url = input('\nEnter the url path of the CGI directory (usually /cgi-bin) :')
    if cgi_url.startswith('/'):
        break
htaccess = """
# this is the .htaccess file for CGI mode
Options -Indexes -MultiViews

ErrorDocument 403 {0}/k_handler.cgi

# rewrite urls so that Karrigell handles all scripts
# excecpt those with static files extension

RewriteEngine On
RewriteCond  %{{SCRIPT_FILENAME}} !\.cgi$
RewriteCond  %{{SCRIPT_FILENAME}} !\.(html|htm|css|js|jpg|jpeg|gif|png)$

RewriteRule (.*) {0}/k_handler.cgi
"""

out = open(os.path.join(local_root_dir,'.htaccess'),'w')
out.write(htaccess.format(cgi_url))
out.close()

# basic index file in folder www
out = open(os.path.join(local_root_dir,'index.py'),'w')
out.write("def index():\n    return 'Karrigell successfully installed'")
out.close()

# if users db defined, add folder admin_tools
if set_users_db.lower() == 'y':
    os.mkdir(os.path.join(local_root_dir,'admin'))
    admin_path = os.path.join(parent,'admin_tools')
    for filename in os.listdir(admin_path):
        shutil.copyfile(os.path.join(admin_path,filename),
            os.path.join(local_root_dir,'admin',filename))

# replace first line of k_handler with the right Python path
lines = open('k_handler.cgi').readlines()
lines[0] = '#!'+python_path+'\n'
out = open(os.path.join(local_cgi_dir,'k_handler.cgi'),'w')
out.writelines(lines)
out.close()

# add Karrigell and HTMLTags modules
for path in ['Karrigell','HTMLTags']:
    abs_path = os.path.join(parent,path)
    os.mkdir(os.path.join(local_cgi_dir,path))
    for filename in os.listdir(abs_path):
        print('add',filename)
        shutil.copyfile(os.path.join(abs_path,filename),
            os.path.join(local_cgi_dir,path,filename))

print("""
The Karrigell distribution was created successfully. Copy/upload the content
of subfolder "cgi_directory" in the CGI directory and the content
of subfolder "root_directory" in the root directory. Then enter
http://<hostname>/<root-url> in a browser. You should see the message
"Karrigell successfully installed" """)

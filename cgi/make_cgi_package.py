import os
import shutil
import datetime

import Karrigell

name = 'Karrigell-{}-cgi'.format(Karrigell.version)
dest_dir = os.path.join(os.getcwd(),'cgi-package')
if os.path.exists(dest_dir):
    shutil.rmtree(dest_dir)
os.mkdir(dest_dir)

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

out = open(os.path.join(dest_dir,'cgi_config.py'),'w')
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

out.write('\n\napps = [App()]\n')

# replace first line of k_handler with the right Python path
lines = open('k_handler.cgi').readlines()
lines[0] = '#!'+python_path+'\n'
out = open(os.path.join(dest_dir,'k_handler.cgi'),'w')
out.writelines(lines)
out.close()

# add Karrigell and HTMLTags modules
parent = os.path.dirname(os.getcwd())
for path in ['Karrigell','HTMLTags']:
    abs_path = os.path.join(parent,path)
    os.mkdir(os.path.join(dest_dir,path))
    for filename in os.listdir(abs_path):
        print('add',filename)
        shutil.copyfile(os.path.join(abs_path,filename),
            os.path.join(dest_dir,path,filename))

# create folder for document root with the .htaccess file and an index file

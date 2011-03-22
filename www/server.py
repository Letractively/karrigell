import os
import Karrigell

# create an application
# by default, root url is / and root directory is this directory
class MyApp(Karrigell.App):

    # set users database
    users_path = os.path.join(os.path.dirname(os.getcwd()),'data','users.sqlite')
    users_db = Karrigell.admin_db.SQLiteUsersDb(users_path)

    # set translation database
    transl_path = os.path.join(os.path.dirname(os.getcwd()),'data','translation.sqlite')
    translation_db = Karrigell.admin_db.SQLiteTranslationDb(transl_path)

# start the web server on port 80 to serve this application
Karrigell.run(apps=[MyApp])

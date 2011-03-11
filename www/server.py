import os
import Karrigell

app = Karrigell.App()
users_path = os.path.join(os.path.dirname(os.getcwd()),'data','users.sqlite')
transl_path = os.path.join(os.path.dirname(os.getcwd()),'data','translation.sqlite')
app.users_db = Karrigell.admin_db.SQLiteUsersDb(users_path)
app.translation_db = Karrigell.admin_db.SQLiteTranslationDb(transl_path)

Karrigell.run(apps=[app])

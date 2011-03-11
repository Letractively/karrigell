import os
import Karrigell
print(Karrigell.__file__)

app = Karrigell.App()
db_path = os.path.join(os.path.dirname(os.getcwd()),'data','users.sqlite')
app.users_db = Karrigell.admin_db.SQLiteUsersDb(db_path)

Karrigell.run(apps=[app])

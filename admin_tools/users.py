Login(role="admin")

import Karrigell.admin_db
banner = Import('banner.py')

levels = list(Karrigell.admin_db.levels.keys())

style = LINK(rel="stylesheet",href="../style.css")

def index():
    body = DIV(Id="container")
    body <= A(_('Home'),href='/')
    body <= banner.banner()
    content = H2(_('Users management'))
    conn = THIS.users_db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT rowid,login,role FROM users')
    table = TABLE(Id="users-table")
    table <= TR(TH('&nbsp;')+TH(_('Login'))+TH(_('Role')))
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        table <= TR(TD(A('Edit',href='edit?rowid={}'.format(row[0])))+
            Sum(TD(x) for x in row[1:]))

    form = FORM(action="new_entry")
    form <= INPUT(Type="submit",value=_("Insert new..."))
    
    content += table + form
    body <= content
    
    return HTML(HEAD(TITLE("Users")+style)+BODY(body))

def edit(rowid):
    conn = THIS.users_db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT login,role FROM users WHERE rowid=?',(rowid,))
    login,role = cursor.fetchone()
    body = A(_('Home'),href='/')
    body += H2(_('Users management'))
    table = TABLE()
    table <= TR(TH(_('Login'))+TD(INPUT(name="login",value=login)))
    table <= TR(TH(_('Role'))+TD(SELECT(name="role").from_list(levels).select(content=role)))

    form = FORM(action="update",method="post")
    form <= table+P()
    form <= INPUT(Type="hidden",name="rowid",value=rowid)
    form <= INPUT(Type="submit",name="action",value=_("Update"))
    form <= INPUT(Type="submit",name="action",value=_("Delete"))
    form <= INPUT(Type="submit",name="action",value=_("Cancel"))
    body += form

    return HTML(HEAD(TITLE(_("Users management"))+style)+BODY(body))

def new_entry():
    body = A(_('Home'),href='/')
    body += H2(_('Users management'))
    table = TABLE()
    table <= TR(TH(_('Login'))+TD(INPUT(name="login")))
    table <= TR(TH(_('Password'))+TD(INPUT(Type="password",name="password")))
    table <= TR(TH(_('Role'))+TD(SELECT(name="role").from_list(levels)))

    form = FORM(action="insert",method="post")
    form <= table
    form <= INPUT(Type="submit",value=_("Insert"))
    body += form
    return HTML(HEAD(TITLE("Users")+style)+BODY(body))

def update(action,rowid,login,role):
    role = levels[int(role)]
    if action == _("Cancel"):
        raise HTTP_REDIRECTION("index")
    conn = THIS.users_db.get_connection()
    cursor = conn.cursor()
    if action == _("Update"):
        cursor.execute("UPDATE users SET login=?,role=? WHERE rowid=?",
            (login,role,rowid))
    elif action == _("Delete"):
        cursor.execute("DELETE FROM users WHERE rowid=?",(rowid,))
    conn.commit()
    raise HTTP_REDIRECTION("index")

def insert(login,password,role):
    role = levels[int(role)]
    conn = THIS.users_db.get_connection()
    cursor = conn.cursor()
    import hashlib
    _hash = hashlib.md5()
    _hash.update(password.encode('utf-8'))
    cursor.execute("INSERT INTO users (login,password,role) VALUES (?,?,?)",
        (login,_hash.digest(),role))
    conn.commit()
    raise HTTP_REDIRECTION("index")

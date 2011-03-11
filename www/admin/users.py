Login(role="admin")

import Karrigell.admin_db
banner = Import('banner.py')

levels = list(Karrigell.admin_db.levels.keys())

style = LINK(rel="stylesheet",href="../style.css")
head = TITLE(_("Users_management"))+style

def index():
    body = DIV(Id="container")
    body <= banner.banner(home=True,title=_("Users management"))
    content = H2(_('Users management'))
    conn = THIS.users_db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT rowid,login,role,created,last_visit,nb_visits \
        FROM users')
    table = TABLE(Id="users-table")
    table <= TR(TH(_('Login'))+TH(_('Role'))+TH(_('Created'))+
        TH(_('Last visit'))+TH(_('Visits')))
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        rowid,login,role,created,last_visit,nb_visits = row
        line = TD(A(login,href='edit?rowid={}'.format(rowid),Class="login"))
        line += TD(role)+TD(created)+TD(last_visit)+TD(nb_visits)
        
        table <= TR(line)

    form = FORM(action="new_entry")
    form <= INPUT(Type="submit",value=_("Insert new..."))
    
    content += table + form
    body <= content
    return HTML(HEAD(head)+BODY(body))

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
    body = DIV(Id="container")
    body <= banner.banner(home=True,title=_("Users management"))

    form_container = DIV(Id="form_container")
    form = FORM(action="insert",method="POST")
    form <= DIV('Login',Class="login_prompt")
    form <= INPUT(name='login',value='')
    form <= DIV(_('Password'),Class="login_prompt")
    form <= INPUT(Type="password",name="password",value='')
    form <= INPUT(Type="submit",value="Ok")
    form_container <= form
    form <= DIV(_('Role'),Class="login_prompt")
    form <= SELECT(name="role").from_list(levels)
    form <= P()+INPUT(Type="submit",value=_("Insert"))
    form_container <= form
    body <= form
    return HTML(HEAD(head)+BODY(body))

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
    try:
        THIS.users_db.add_user(login,password,role)
        raise HTTP_REDIRECTION("index")
    except ValueError as msg:
        body = DIV(Id="container")
        body <= banner.banner(home=True,title=_("Users management"))
        content = H2(_('Users management'))
        content += msg
        body <= content
        return HTML(HEAD(head)+BODY(body))
    
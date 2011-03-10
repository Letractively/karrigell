import datetime
banner = Import('banner.py')

lifetime = 30 # how long a cookie lasts, in days

style = LINK(rel="stylesheet",href="../style.css")

def login(role,origin):
    container = DIV(Id="container")
    container <= banner.banner()
    
    if THIS.users_db is None:
        container <= 'No users database declared for this application'
    elif THIS.users_db.is_empty():
        container <= H4("Users database is empty. "
            "Set administrator login and password")
        form_container = DIV(Id="form_container")
        form = FORM(action="set_admin",method="POST")
        form <= INPUT(Type="hidden",name="origin",value=origin)
        form <= DIV('Login',Class="login_prompt")
        form <= INPUT(name='login')
        form <= DIV(_('Password'),Class="login_prompt")
        form <= INPUT(Type="password",name="password")
        form <= INPUT(Type="submit",value="Ok")
        form_container <= form
        container <= form_container
    else:
        form_container = DIV(Id="form_container")
        form = FORM(action="check_login",method="POST")
        form <= INPUT(Type="hidden",name="origin",value=origin)
        form <= INPUT(Type="hidden",name="required_role",value=role)
        form <= DIV('Login',Class="login_prompt")
        form <= INPUT(name='login')
        form <= DIV(_('Password'),Class="login_prompt")
        form <= INPUT(Type="password",name="password")
        save = DIV(Class="remember_prompt")
        save <= _('Remember me')
        save <= INPUT(Type="checkbox",name="remember")
        form <= save
        form <= INPUT(Type="submit",value="Ok")
        form_container <= form
        container <= form_container

    return HTML(HEAD(TITLE('Login')+style)+BODY(container))

def _set_cookies(remember,login,password):
    SET_COOKIE[THIS.login_cookie] = login
    SET_COOKIE[THIS.login_cookie]['path'] = THIS.root_url
    if remember: # persistent cookie
        import datetime
        new = datetime.date.today() + datetime.timedelta(days = lifetime) 
        SET_COOKIE[THIS.login_cookie]['expires'] = new.strftime("%a, %d-%b-%Y 23:59:59 GMT")
        SET_COOKIE[THIS.login_cookie]['max-age'] = lifetime*24*3600 # seconds

    import random
    import string
    skey = ''.join(random.choice(list(string.ascii_letters+string.digits))
        for i in range(16))
    THIS.users_db.set_session_key(login,skey)
    SET_COOKIE[THIS.skey_cookie] = skey
    SET_COOKIE[THIS.skey_cookie]['path'] = THIS.root_url
    if remember: # cookie will live 30 days
        SET_COOKIE[THIS.skey_cookie]['expires'] = \
            new.strftime("%a, %d-%b-%Y 23:59:59 GMT")
        SET_COOKIE[THIS.skey_cookie]['max-age'] = lifetime*24*3600 # seconds

def check_login(required_role,origin,login,password,remember=False):
    db = THIS.users_db
    if db.user_has_role(login,password,required_role):
        _set_cookies(remember,login,password)
    raise HTTP_REDIRECTION(origin)

def set_admin(origin,login,password):
    if not THIS.users_db.is_empty():
        raise HTTP_ERROR(500,'db not empty')
    THIS.users_db.set_admin(login,password)
    _set_cookies(False,login,password)
    raise HTTP_REDIRECTION(origin)
Login("admin")
banner = Import('banner.py')

def index():
    head = HEAD()
    head <= TITLE('Karrigell - '+_('Administration tools'))
    head <= LINK(rel="stylesheet",href="../style.css")
    container = DIV(Id="container")
    container <= banner.banner()
    container <= A(_('Users management'),href="../users.py")
    container <= BR()+A(_('Translations'),href="../translations.py")
    return HTML(head+BODY(container))   

def logout():
    Logout()
    
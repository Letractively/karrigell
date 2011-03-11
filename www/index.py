banner = Import('admin/banner.py')

def index():
    head = LINK(rel="stylesheet",href="/admin/style.css")
    head += TITLE('Karrigell home page')
    container = DIV(Id="container")
    container <= banner.banner(title = _("Home"))
    container <= "Karrigell is installed"
    container <= BR()+A("Administration",href="/admin/index.py")
    return HTML(HEAD(head)+BODY(container))
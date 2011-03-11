banner = Import('admin/banner.py')

def index():
    head = LINK(rel="stylesheet",href="/admin/style.css")
    head += TITLE('Karrigell home page')
    container = DIV(Id="container")
    container <= banner.banner(title = _("Home"))
    content = DIV(Id="content")
    content <= "Karrigell is installed"
    content <= BR()+A("Administration",href="/admin/index.py")
    container <= content
    return HTML(HEAD(head)+BODY(container))
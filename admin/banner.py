def banner():
    bandeau = DIV(Id="bandeau")
    home = A(_("Home"),href='../',Class="banner")
    bandeau <= DIV(home+' Karrigell - '+_('Administration tools'),Class="page_title")
    if THIS.login_cookie in COOKIE:
        log = COOKIE[THIS.login_cookie].value+'&nbsp;&nbsp;'
        log += A(_("Logout"),href="logout",Class="banner")
        bandeau <= DIV(log,Class="login")
    return bandeau
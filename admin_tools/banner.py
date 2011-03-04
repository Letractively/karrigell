def banner():
    bandeau = DIV(Id="bandeau")
    bandeau <= DIV('Karrigell - '+_('Administration tools'),Class="page_title")
    if THIS.login_cookie in COOKIE:
        log = COOKIE[THIS.login_cookie].value+'&nbsp;&nbsp;'
        log += A(_("Logout"),href="logout",Class="logout")
        bandeau <= DIV(log,Class="login")
    return bandeau
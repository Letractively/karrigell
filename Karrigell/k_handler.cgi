#!python

import os
import sys
import email
import datetime

class Server:
    pass

try:
    import Karrigell
    import cgi_config
    
    class RequestHandler(Karrigell.RequestHandler):

        apps = cgi_config.apps
        alias = dict((app.root_url[1:],app) for app in apps)

        def __init__(self, request, client_address):
            env = os.environ
            self.server = Server()
            self.server.host = os.environ["SERVER_NAME"]
            self.server.port = os.environ["SERVER_PORT"]
            self.server_version = os.environ["SERVER_SOFTWARE"]
            self.sys_version = sys.version
            self.request, self.client_address = request, client_address
            self.sock = request
            self.wfile = sys.stdout.buffer # bytes
            self.rfile = sys.stdin

            # headers
            self.headers = email.message.Message()
            for k in os.environ:
                if k.startswith("HTTP_"):
                    header = k[5:].replace('_','-')
                    self.headers.add_header(header,os.environ[k])

            self.path = os.environ["REQUEST_URI"]
            self.request_version = env["SERVER_PROTOCOL"]
            self.protocol = env["SERVER_PROTOCOL"]
            self.requestline = "%s %s %s" %(env["REQUEST_METHOD"],
                env["REQUEST_URI"],env["SERVER_PROTOCOL"])
            self.method = env["REQUEST_METHOD"]
            self.command = self.method
            if self.method in ['GET','POST']:
                command = getattr(self,'do_'+self.method)
                command()

        def send_response(self, code, message=None):
            """Don't send response code : Apache sends 200 Ok, 
            except if a Status header is sent
            """
            if code == 200:
                return
            if message is None:
                message = self.responses[code][0]
            self.send_header('Status',
                    '%s %s' %(code,message))

    # on windows all \n are converted to \r\n if stdout is a terminal 
    # and is not set to binary mode
    # this will then cause an incorrect Content-length.
    if sys.platform == "win32":
        import  msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    client_address = (os.environ["REMOTE_ADDR"],int(os.environ["REMOTE_PORT"]))

    handler = RequestHandler(sys.stdin,client_address)
    """for app in apps:
        if app.users_db is not None and app.users_db.is_empty():
            print('Users database %s is empty for app at %s'
                %(app.users_db.name,app.root_url))
            print('Set login and password for administrator')
            while True:
                login = input('Login : ')
                if login:
                    break
            while True:
                password = input('Password : ')
                if len(password)<6 or password==login:
                    print('Password must have at least 6 characters and must ')
                    print('be different from login')
                else:
                    break
            app.users_db.set_admin(login,password)"""

    handler.handle_data()

except:
    import traceback
    import io
    out = io.StringIO()
    traceback.print_exc(file=out)
    print("Content-Type: text/plain;")
    print()
    print(out.getvalue())

    print("\n".join(sys.path))
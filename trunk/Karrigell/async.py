import socket
import asyncore
import asynchat
import email.message
import http.server,http.client
import io
import Karrigell
import Karrigell.check_apps

class HTTP(asynchat.async_chat):

    def __init__(self,sock=None,map=None):
        asynchat.async_chat.__init__(self,sock,map)
        self.terminator = b'\r\n\r\n'
    
    def collect_incoming_data(self,data):
        self.incoming.append(data)

    def found_terminator(self):
        print('found terminator',len(self.terminator),self.ac_in_buffer)
        self.request_line = self.incoming.pop()
        print('request line',self.request_line)
        self.terminator = None
        #self.headers = email.message.Message(b''.join(self.incoming))
        print('headers ok')
        self.push(b'HTTP/1.1 200 Ok\r\n')
        self.push(b'Content-type: text/html\r\n\r\n')
        self.push(b'ca marche')

class http_request_handler(asynchat.async_chat,Karrigell.RequestHandler):

    def __init__(self, sock, client_address, sessions, log):
        asynchat.async_chat.__init__(self, sock=sock)
        self.client_address = client_address
        self.sessions = sessions
        self.log = log
        self.reset_values()

    def reset_values(self):
        self.ibuffer = []
        self.obuffer = b""
        self.set_terminator(b"\r\n\r\n")
        self.reading_headers = True
        self.handling = False
        self.cgi_data = None

    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer.append(data)

    def found_terminator(self):
        if self.reading_headers:
            self.reading_headers = False
            lines = b''.join(self.ibuffer).split(b'\r\n')
            self.raw_requestline = lines.pop(0).decode('ascii')
            self.protocol,self.command,self.path = self.raw_requestline.split()
            rfile = io.BytesIO(b'\r\n'.join(lines)+b'\r\n\r\n')
            print(rfile.getvalue())
            rfile.seek(0)
            print('rfile',rfile)
            self.headers = http.client.parse_headers(rfile)
            self.ibuffer = []
            if self.command.upper() == b"POST":
                clen = self.headers.getheader("content-length")
                self.set_terminator(int(clen))
            else:
                self.handling = True
                self.set_terminator(None)
                self.do_GET()
        elif not self.handling:
            self.set_terminator(None) # browsers sometimes over-send
            self.cgi_data = parse(self.headers, b"".join(self.ibuffer))
            self.handling = True
            self.ibuffer = []
            self.handle_request()

    def handle_request(self):
        self.push(b'HTTP/1.1 200 Ok\r\n')
        self.push(b'Content-type: text/html\r\n')
        self.push(b'Content-length: 9\r\n')
        self.push(b'\r\n')
        self.push(b'ca marche')
        self.reset_values()

class Server(asynchat.async_chat):

    def handle_read(self):
        try:
            sock,client_address = self.socket.accept()
            sock.setblocking(0)
        except socket.error:
            return
        self.handler(sock,client_address,None,None)

def run(handler=http_request_handler,port=80,apps=[Karrigell.App]):
    use_ipv6 = False
    Karrigell.check_apps.check(apps)
    handler.apps = apps
    handler.alias = dict((app.root_url.lstrip('/'),app)
        for app in apps)
    sock = socket.socket((socket.AF_INET, socket.AF_INET6)[use_ipv6],
                              socket.SOCK_STREAM)
    # for 'Address already in use' 
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    sock.setblocking(0)
    sock.bind(('',port))
    sock.listen(5)
    server = Server(sock)
    server.handler = handler
    print("Server running on port {}".format(port))
    asyncore.loop()

if __name__=="__main__":
    run(port=8000)
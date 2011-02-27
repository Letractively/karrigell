"""Script server based on http.server

Handles GET and POST requests, on-disk session management,
HTTP redirection

Python scripts are executed in a namespace made of :
- REQUEST_HEADERS : the http request headers sent by user agent
- http.cookies : cookies sent by user agent
- RESPONSE_HEADERS : the http response headers
- SET_COOKIE : used to set cookies for user agent
- ENCODING : determines the Unicode encoding used by user agent
- Template(url,encoding,*args,**kw) : return the file at specified url, used
  standard Python string formatting (method format() for strings)
- HTTP_REDIRECTION : an exception to raise if the script wants to redirect
to a specified URL (raise HTTP_REDIRECTION, url)
- Import() : replacement for built-in import for user-defined modules
- Session() : a function returning the session object
- THIS : instance of the request handler

Parameters passed to the server
- root : document root
- port : server port
- filters : a list of functions taking the request handler as single
  argument. A function
    . returns None if no action should be done. Execute next funtion
    . returns a path in the file system (typically if the url starts
      with an alias)
    . raises Error(msg) where msg is a 2-element tuple (code,message),
      typically (403,"Permission denied") if the folder is protected
      and/or the user doesn't have the requested access rights
- session_dir : directory for session object files
"""

import sys
import os
import re
import string
import io
import pickle
import marshal
import threading
import random
import traceback
import datetime

import urllib.parse
import urllib
import cgi
import http.server
import http.cookies
import email.utils
import email.message

import Karrigell.users_db

version = "4.0"

def _log(*data):
    for item in data:
        sys.stderr.write('%s\n' %item)

chars = string.ascii_letters + string.digits
def generate_random(length):
    """Return a random string of specified length (used for session id's)"""
    return ''.join([random.choice(chars) for i in range(length)])

# lock for thread-safe session storage
rlock = threading.RLock()

class SessionElement(dict):

    def __setitem__(self,key,value):
        try:
            marshal.dumps(value)
        except ValueError:
            msg = 'Bad type for session object key %s ' %key
            msg += ': expected built-in type, got %s' %value.__class__
            raise ValueError(msg)
        dict.__setitem__(self,key,value)

class HTTP_REDIRECTION(Exception):
    pass

class Error(Exception):
    pass

class RequestHandler(http.server.CGIHTTPRequestHandler):
    """One instance of this class is created for each HTTP request"""

    name = 'Karrigell'
    filters = []
    root = os.getcwd()
    session_dir = os.path.join(root,"sessions")
    login_cookie = 'login'
    login_session_key = 'skey'
    alias = {}
    users_db = None
    
    def do_GET(self):
        """Begin serving a GET request"""
        # build self.body from the query string
        self.elts = urllib.parse.urlparse(self.path)
        self.body = urllib.parse.parse_qs(self.elts[4], keep_blank_values=1)
        for key in self.body:
            self.body[key] = self.body[key][0]
        self.handle_data()

    def do_POST(self):
        """Begin serving a POST request. The request data is readable
        on a file-like object called self.rfile"""
        self.elts = urllib.parse.urlparse(self.path)
        body = self.get_body()
        data = {}
        # If field name ends with [], always return a list of values
        # Otherwise, return a value, or the item with attributes
        # 'file' and 'filename' for file uploads
        for k in body.keys():
            if isinstance(body[k],list): # several fields with same name
                if k.endswith('[]'):
                    data[k[:-2]] = [x.value for x in body[k]]
            else:
                if body[k].filename: # file upload : don't read the value
                    data[k] = body[k]
                else:
                    if k.endswith('[]'):
                        data[k[:-2]] = [body[k].value]
                    else:
                        data[k] = body[k].value
        self.body = data
        self.handle_data()

    def get_body(self):
        return cgi.FieldStorage(self.rfile,headers=self.headers,
            environ={'REQUEST_METHOD':'POST'})

    def handle_data(self):
        """Process the data received"""
        # prepare data dictionary
        self.resp_headers = email.message.Message()
        self.resp_headers.add_header("Content-type",'text/html') # default
        self.cookies = http.cookies.SimpleCookie() # received http.cookies
        if 'cookie' in self.headers:
            self.cookies = http.cookies.SimpleCookie(self.headers.get("cookie"))
        self.set_cookie = http.cookies.SimpleCookie() # returned http.cookies
        self.encoding = sys.getdefaultencoding() # Unicode encoding
        try:
            fs_path = self.get_file(self.elts[2])
        except Exception as msg:
            code,expl = msg.message
            return self.send_error(code,expl)
        if fs_path is None:
            return self.send_error(403,'Permission denied')
        elts = list(self.elts)
        if os.path.isdir(fs_path):  # url matches a directory
            if self.users_db is not None: # control access rights
                level,login_url = self.users_db.infos(self.elts[2])
                if level == 'None':
                    return self.send_error(403,'Permission denied')
                elif level != 'All':
                    if not self.users_db.is_valid(self.cookies,level):
                        if login_url:
                            return self.redir(login_url+
                                '?origin='+urllib.parse.quote(self.elts[2]))
                        else:
                            return self.send_error(403,'Permission denied')
            if not elts[2].endswith('/'):
                elts[2] += '/'
                return self.redir(urllib.parse.urlunparse(elts))
            if os.path.exists(os.path.join(fs_path,'index.py')):
                elts[2] += 'index.py/index'
                return self.redir(urllib.parse.urlunparse(elts))
            elif os.path.exists(os.path.join(fs_path,'index.html')):
                elts[2] += 'index.html'
                return self.redir(urllib.parse.urlunparse(elts))
            else:
                # list directory
                dir_list = self.list_directory(fs_path) # send resp + headers
                self.copyfile(dir_list, self.wfile)
                return
        ext = os.path.splitext(fs_path)[1].lower()
        if ext.lower()=='.py':
            elts[2] += '/index'
            # redirect to function index of script
            return self.redir(urllib.parse.urlunparse(elts))
        script_path,func = fs_path.rsplit(os.sep,1)
        if os.path.splitext(script_path)[1] == '.py':
            # Python script called with a function name
            if func.startswith('_'): # private function
                self.send_error(500,'Server error')
                return
            self.url_path = elts[2]
            self.script_path = script_path
            try:
                self.run(func)
            except:
                self.resp_headers.replace_header('Content-type','text/plain')
                result = io.StringIO()
                traceback.print_exc(file=result)
                result = io.BytesIO(result.getvalue().encode('ascii','ignore'))
                return self.done(200,result)
        else:
            # other files
            try:
                f = open(fs_path,'rb')
            except IOError:
                self.send_error(404, "File not found")
                return
            # use browser cache if possible
            if "If-Modified-Since" in self.headers:
                ims = email.utils.parsedate(self.headers["If-Modified-Since"])
                if ims is not None:
                    ims_datetime = datetime.datetime(*ims[:7])
                    ims_dtstring = ims_datetime.strftime("%d %b %Y %H:%M:%S")
                    last_modif = datetime.datetime.utcfromtimestamp(
                        os.stat(fs_path).st_mtime).strftime("%d %b %Y %H:%M:%S")
                    if last_modif == ims_dtstring:
                        self.done(304,io.BytesIO())
                        return
            ctype = self.guess_type(fs_path)
            self.resp_headers.replace_header('Content-type',ctype)
            self.resp_headers['Content-length'] = \
                str(os.fstat(f.fileno())[6])
            self.resp_headers["Last-modified"] = \
                self.date_time_string(os.stat(fs_path).st_mtime)
            self.done(200,f)

    def redir(self,url):
        # redirect to the specified url
        self.resp_headers['Location'] = url
        self.done(301,io.BytesIO())

    def get_file(self,path):
        """Return a file name matching path"""
        for func in self.filters:
            res = func(self)
            if res is not None:
                return res
        # default : built path from root dir and url elements
        elts = urllib.parse.unquote(path).split('/')
        if elts[0] in self.alias:
            return os.path.join(self.alias[elts[0]],*elts[1:])
        return os.path.join(self.root,*elts)

    def erase_cookie(self,name):
        self.set_cookie[name] = ''
        self.set_cookie[name]['path'] = '/'
        new = datetime.date.today() + datetime.timedelta(days = -10) 
        self.set_cookie[name]['expires'] = \
            new.strftime("%a, %d-%b-%Y 23:59:59 GMT")
        self.set_cookie[name]['max-age'] = 0

    def login(self,role='admin'):
        if not self.users_db.is_valid(self.cookies,role):
            self.redir(self.login_url+'?origin='+self.path)

    def logout(self,redir_to=None):
        if redir_to is None:
            redir_to = urllib.parse.urljoin(self.path,'index')
        self.erase_cookie(self.login_cookie)
        self.erase_cookie(self.login_session_key)
        self.redir(redir_to)

    def abs_path(self,*rel_path):
        return os.path.join(os.path.dirname(self.script_path),*rel_path)

    def abs_url(self,rel_url):
        base = self.url_path
        return urllib.parse.urljoin(base[:base.rfind('/')],rel_url)

    def run(self,func):
        """Run function func in a Python script
        Function arguments are key/values in request body or query string"""
        # initialize the execution namespace for the script
        self.namespace = {'REQUEST_HEADERS' : self.headers,
            'RESPONSE_HEADERS':self.resp_headers,
            'HTTP_REDIRECTION':HTTP_REDIRECTION,
            'COOKIE':self.cookies,'SET_COOKIE':self.set_cookie,
            'ENCODING':self.encoding,
            'Template':self.template,'Session':self.Session,
            'Logout':self.logout,'Login':self.login,
            'Import':self._import,'THIS': self }
        import HTMLTags
        for k in dir(HTMLTags):
            if not k.startswith('_'):
                self.namespace[k] = getattr(HTMLTags,k)
        try:
            fileobj = open(self.script_path)
            src = '\n'.join([ x.rstrip() for x in fileobj.readlines()])
            fileobj.close()
            exec(src,self.namespace) # run script in namespace
            if not func in self.namespace:
                msg = 'Server error - no function %s in script %s' \
                    %(func,os.path.basename(self.script_path))
                self.done(500,io.BytesIO(msg.encode(self.encoding)))
                return
            # run function with self.body as argument
            result = self.namespace[func](**self.body) # string or bytes
            self.save_session()
        except HTTP_REDIRECTION as url:
            self.save_session()
            return self.redir(url)

        encoding = self.namespace['ENCODING']
        if not "charset" in self.resp_headers["Content-type"]:
            if encoding is not None:
                ctype = self.resp_headers["Content-type"]
                self.resp_headers.replace_header("Content-type",
                    ctype + "; charset=%s" %encoding)
        output = io.BytesIO()
        if isinstance(result,bytes):
            output.write(result)
        elif isinstance(result,str):
            try:
                output.write(result.encode(encoding))
            except UnicodeEncodeError:
                msg = io.StringIO()
                traceback.print_exc(file=msg)
                return self.done(500,io.BytesIO(msg.getvalue().encode('ascii')))
        else:
            output.write(str(result).encode(encoding))
            
        self.resp_headers['Content-length'] = output.tell()
        self.done(200,output)

    def template(self,tmpl_url,encoding='utf-8',*args,**kw):
        """Templating : format the sting read from the file matching tmpl_url, 
        with the specified encoding and arguments args and kw"""
        fs_path = self.get_file(self.abs_url(tmpl_url))
        fileobj = open(fs_path,encoding=encoding)
        data = fileobj.read()
        fileobj.close()
        return data.format(*args,**kw)

    def _import(self,url):
        """import by url - in threaded environments, "import" is unsafe
        Returns an object whose names are those of the module at this url"""
        fs_path = self.get_file(self.abs_url(url))
        # update builtins so that imported scripts use script namespace
        __builtins__.update(self.namespace)
        ns = {'__builtins__':__builtins__}
        fileobj = open(fs_path)
        exec(fileobj.read(),ns)
        fileobj.close()
        class Imported:
            def __init__(self,ns):
                for k,v in ns.items():
                    setattr(self,k,v)
        return Imported(ns)

    def save_session(self):
        """Save session object as a dictionary"""
        if hasattr(self,'session_object'):
            rlock.acquire() # thread safety
            try:
                session_file = os.path.join(self.session_dir,self.session_id)
                pickle.dump(dict(self.session_object),open(session_file,'wb'))
            except:
                traceback.print_exc(file=self.output)
            rlock.release()

    def Session(self):
        """Get session object matching session_id http.cookies
        If no session_id http.cookies was received, generate one and return an
        empty SessionElement instance"""
        # directory for session files
        if not os.path.exists(self.session_dir):
            os.mkdir(self.session_dir)
        if hasattr(self,'session_object'):
            return self.session_object
        if "session_id" in self.cookies:
            self.session_id = self.cookies["session_id"].value
        else:
            self.session_id = generate_random(8)
            self.set_cookie["session_id"] = self.session_id
        session_file = os.path.join(self.session_dir,self.session_id)
        try:
            try:
                rlock.acquire()
                self.session_object = SessionElement(pickle.load(open(session_file,'rb')))
            except (IOError,AttributeError):
                self.session_object = SessionElement()
                pickle.dump({},open(session_file,'wb'))
        finally:
            rlock.release()
        return self.session_object

    def done(self, code, infile):
        """Send response, cookies, response headers + 
        the *bytes* read from infile"""
        self.send_response(code)
        if code == 500:
            self.resp_headers.replace_header('Content-Type','text/plain')
        for (k,v) in self.resp_headers.items():
            self.send_header(k,v)
        for morsel in self.set_cookie.values():
            self.send_header('Set-Cookie', morsel.output(header='').lstrip())
        self.end_headers()
        infile.seek(0)
        self.copyfile(infile, self.wfile)
        self.wfile.flush()

def run(handler=RequestHandler,port=80,root=os.getcwd(),filters=[],
    users_db=None,login_url='/login.py/login'):
    import socketserver
    handler.root = root
    handler.filters = filters
    handler.users_db = users_db
    handler.login_url = login_url
    if users_db is not None and users_db.is_empty():
        print('Users database is empty')
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
        users_db.set_admin(login,password)    
    s=socketserver.ThreadingTCPServer(('',port),handler)
    print("%s %s running on port %s" %(handler.name,version,port))
    s.serve_forever()

def run_app(host="http://localhost",*args,**kw):
    """Start the server in a thread, then open a web browser"""
    class Launcher(threading.Thread):
        def run(self):
            run(*args,**kw)
    Launcher().start()
    import webbrowser
    webbrowser.open(host)

if __name__=="__main__":
    # launch the server on the specified port
    extensions = ['.pdl']
    def no_extensions(handler):
        for ext in extensions:
            if handler.path.endswith(ext):
                raise Error((403,'Permission denied'))

    transl = {'doc':r'c:\Mes documents\Pierre\Essai DHTML'}
    def alias(handler):
        elts = handler.path.lstrip('/').split('/')
        print(elts)
        if elts[0] in transl:
            return os.path.join(transl[elts[0]],*elts[1:])

    run(port=80,#r'c:\Karrigell-dev',
        filters=[no_extensions,alias]
        )

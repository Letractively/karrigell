"""Karrigell server and request handler

Python scripts are executed in a namespace made of :
- REQUEST_HEADERS : the http request headers sent by user agent
- COOKIE : cookies sent by user agent
- RESPONSE_HEADERS : the http response headers
- SET_COOKIE : used to set cookies for user agent
- ENCODING : determines the Unicode encoding used by user agent
- Template(url,encoding,*args,**kw) : return the file at specified url, uses
  standard Python string formatting (method format() for strings)
- HTTP_REDIRECTION : an exception to raise if the script wants to redirect
to a specified URL : raise HTTP_REDIRECTION(url)
- Import() : replacement for built-in import for user-defined modules
- Session() : a function returning the session object
- THIS : instance of the request handler
"""

import sys
import os
import re
import string
import io
import random
import traceback
import datetime

import urllib.parse
import cgi
import http.server
import http.cookies
import email.utils
import email.message

import Karrigell.sessions

version = "4.1"

class HTTP_REDIRECTION(Exception):
    pass

class HTTP_ERROR(Exception):

    def __init__(self,code,message=None):
        self.code = code
        self.message = message

class RequestHandler(http.server.CGIHTTPRequestHandler):
    """One instance of this class is created for each HTTP request"""

    name = 'Karrigell'
    
    def do_GET(self):
        """Begin serving a GET request"""
        # build self.body from the query string
        self.elts = urllib.parse.urlparse(self.path)
        data = urllib.parse.parse_qs(self.elts[4], keep_blank_values=1)
        self.body = {}
        for key in data:
            if key.endswith('[]'):
                self.body[key[:-2]] = data[key]
            else:
                self.body[key] = data[key][0]
        self.handle_data()

    def do_POST(self):
        """Begin serving a POST request"""
        self.elts = urllib.parse.urlparse(self.path)
        body = cgi.FieldStorage(self.rfile,headers=self.headers,
            environ={'REQUEST_METHOD':'POST'}) # read POST data from self.rfile
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

    def handle_data(self):
        """Process the data received"""
        # received cookies
        self.cookies = http.cookies.SimpleCookie(self.headers.get("cookie",None))
        # initialize response headers and cookies
        self.resp_headers = email.message.Message()
        self.resp_headers.add_header("Content-type",'text/html') # default
        self.set_cookie = http.cookies.SimpleCookie() # cookies to return to user
        self.encoding = sys.getdefaultencoding() # Unicode encoding
        
        self.path_info = self.elts[2] # equivalent of CGI PATH_INFO
        elts = urllib.parse.unquote(self.path_info).split('/')
        # identify the application and set attributes from it
        app = self.alias.get(elts[1],self.alias[''])
        for attr in ['root_url','root_dir','users_db','translation_db']:
            setattr(self,attr,getattr(app,attr))
        self.login_url = app.get_login_url()
        self.session_storage = app.session_storage_class(app)
        self.login_cookie,self.skey_cookie = app.get_cookie_names()
        
        # apply application filters
        filtered = None
        for func in app.filters:
            try:
                filtered = func(self)
            except HTTP_REDIRECTION as url:
                redir_to = str(url)
                return self.redir(redir_to)
            except HTTP_ERROR as msg:
                return self.send_error(msg.args[0])
            except:
                return self.print_exc()
        # if no filter returned a value other than None, use default
        fs_path = filtered or self.get_file(self.elts[2])
        elts = list(self.elts)
        if os.path.isdir(fs_path):  # url matches a directory
            if not elts[2].endswith('/'):
                elts[2] += '/'
                return self.redir(urllib.parse.urlunparse(elts))
            if os.path.exists(os.path.join(fs_path,'index.py')):
                elts[2] += 'index.py/index'
                return self.redir(urllib.parse.urlunparse(elts))
            elif os.path.exists(os.path.join(fs_path,'index.html')):
                elts[2] += 'index.html'
                return self.redir(urllib.parse.urlunparse(elts))
            else:  # list directory
                dir_list = self.list_directory(fs_path) # send resp + headers
                return self.copyfile(dir_list, self.wfile)
        ext = os.path.splitext(fs_path)[1].lower()
        if ext.lower()=='.py':
            # redirect to function index of script
            elts[2] += '/index'
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
                return self.print_exc()
        else: # other files than Python scripts
            try:
                f = open(fs_path,'rb')
            except IOError:
                return self.send_error(404, "File not found")
            # use browser cache if possible
            if "If-Modified-Since" in self.headers:
                ims = email.utils.parsedate(self.headers["If-Modified-Since"])
                if ims is not None:
                    ims_datetime = datetime.datetime(*ims[:7])
                    ims_dtstring = ims_datetime.strftime("%d %b %Y %H:%M:%S")
                    last_modif = datetime.datetime.utcfromtimestamp(
                        os.stat(fs_path).st_mtime).strftime("%d %b %Y %H:%M:%S")
                    if last_modif == ims_dtstring:
                        return self.done(304,io.BytesIO())
            ctype = self.guess_type(fs_path)
            self.resp_headers.replace_header('Content-type',ctype)
            self.resp_headers['Content-length'] = str(os.fstat(f.fileno())[6])
            self.resp_headers["Last-modified"] = \
                self.date_time_string(os.stat(fs_path).st_mtime)
            self.done(200,f)

    def print_exc(self):
        # print exception
        self.resp_headers.replace_header('Content-type','text/plain')
        result = io.StringIO()
        traceback.print_exc(file=result)
        result = io.BytesIO(result.getvalue().encode('ascii','ignore'))
        self.done(200,result)

    def redir(self,url):
        # redirect to the specified url
        self.resp_headers['Location'] = url
        self.done(301,io.BytesIO())

    def get_file(self,path):
        """Return a file name matching path"""
        elts = urllib.parse.unquote(path).split('/')
        if elts[1] in self.alias:
            return os.path.join(self.root_dir,*elts[2:])
        return os.path.join(self.root_dir,*elts)

    def erase_cookie(self,name):
        self.set_cookie[name] = ''
        self.set_cookie[name]['path'] = self.root_url
        new = datetime.date.today() + datetime.timedelta(days = -10) 
        self.set_cookie[name]['expires'] = \
            new.strftime("%a, %d-%b-%Y 23:59:59 GMT")
        self.set_cookie[name]['max-age'] = 0

    def login(self,role='admin',login_url=None):
        """If user is logged in with specified role, do nothing, else
        redirect to login_url"""
        login_url = login_url or self.login_url
        if not self.users_db:
            raise HTTP_ERROR(500,"Can't login, no users database set")
        elif not self.role(role):
            self.redir(login_url+'?role='+role+'&origin='+self.path)

    def logout(self,redir_to=None):
        """Log out = erase login and session key cookies, then redirect"""
        redir_to = redir_to or urllib.parse.urljoin(self.path_info,'index')
        self.erase_cookie(self.login_cookie)
        self.erase_cookie(self.skey_cookie)
        self.redir(redir_to)

    def role(self,required_role=None):
        """If required_role is None, return user role, or False if user is not
        identified. Else, return True if user has at least the required role"""
        if self.users_db is None:
            raise HTTP_ERROR(500,"Can't get user role, no users database set")
        if not self.skey_cookie in self.cookies:
            return False
        skey = self.cookies[self.skey_cookie].value
        if required_role is None: # return role as string
            return self.users_db.get_role(skey)
        else: # return a boolean : user has a level >= requested role
            return self.users_db.key_has_role(skey,required_role)

    def translation(self,src,language=None):
        """Return the translation of string src in the specified language. If
        language not specified, use the browsers language order"""
        if self.translation_db is not None:
            if language is None:
                langs = self.namespace['ACCEPTED_LANGUAGES']
                if langs:
                    language = langs.split(",")[0].split(";")[0][:2]
            trans = self.translation_db.get_translation(src,language)
            return trans or src
        return src

    def abs_path(self,*rel_path):
        """Return absolute path in the file system, relative to script path"""
        return os.path.join(os.path.dirname(self.script_path),*rel_path)

    def abs_url(self,rel_url):
        base = self.url_path
        return urllib.parse.urljoin(base[:base.rfind('/')],rel_url)

    def run(self,func):
        """Run function func in a Python script
        Function arguments are key/values in request body or query string"""
        # initialize script execution namespace
        self.namespace = {'REQUEST_HEADERS' : self.headers,
            'ACCEPTED_LANGUAGES':self.headers.get("accept-language",None),
            'RESPONSE_HEADERS':self.resp_headers,
            'HTTP_REDIRECTION':HTTP_REDIRECTION,
            'COOKIE':self.cookies,'SET_COOKIE':self.set_cookie,
            'ENCODING':self.encoding,'_':self.translation,
            'Template':self.template,'Session':self.Session,
            'Logout':self.logout,'Login':self.login,
            'Import':self._import,'THIS': self }
        # import names from HTMLTags
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
                msg = 'No function %s in script %s' \
                    %(func,os.path.basename(self.script_path))
                self.done(500,io.BytesIO(msg.encode(self.encoding)))
                return
            # run function with self.body as argument
            result = self.namespace[func](**self.body) # string or bytes
            self.session_storage.save(self)
        except HTTP_REDIRECTION as url:
            self.session_storage.save(self)
            return self.redir(url)
        except HTTP_ERROR as msg:
            return self.send_error(msg.code,msg.message)
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
        """Import by url - in threaded environments, "import" is unsafe
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

    def Session(self):
        """Get session object matching session_id cookie
        If no session_id cookie was received, generate one and return an
        empty SessionElement instance"""
        if hasattr(self,'session_object'):
            return self.session_object
        if "session_id" in self.cookies:
            self.session_id = self.cookies["session_id"].value
        else:
            chars = string.ascii_letters + string.digits
            self.session_id = ''.join([random.choice(chars) for i in range(16)])
            self.set_cookie["session_id"] = self.session_id
        self.session_object = self.session_storage.get(self.session_id)
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

class App:
    """Application parameters"""    
    root_url = '/'
    login_url = None
    root_dir = os.getcwd()
    session_storage_class = Karrigell.sessions.FileSessionStorage
    users_db = None
    translation_db = None
    filters = []
    # names for login and session key cookies. Should be application specific
    login_cookie = None
    skey_cookie = None

    def get_login_url(self):
        return self.login_url or \
                self.root_url.rstrip('/')+'/login.py/login'

    def get_cookie_names(self):
        suffix = self.root_url[1:].replace('/','_')
        login_cookie = self.login_cookie or 'login_'+suffix
        skey_cookie = self.skey_cookie or 'skey_'+suffix
        return login_cookie,skey_cookie

def run(handler=RequestHandler,port=80,apps=[App()]):
    import socketserver
    for app in apps:
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
            app.users_db.set_admin(login,password)
    handler.apps = apps
    handler.alias = dict((app.root_url[1:],app) for app in apps)
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
    run()
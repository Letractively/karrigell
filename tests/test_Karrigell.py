import sys
import os

# modify sys.path to use this version of Karrigell
cwd = os.getcwd()
sys.path.insert(0,os.path.join(os.path.dirname(cwd),'trunk'))

import Karrigell
# also import HTMLTags, so that the name "HTMLTags" will be in 
# sys.modules when Karrigell imports it
import HTMLTags

import threading
import unittest
import urllib.request
import http.cookies

template = """<html>
<head>
<title>template test</title>
</head>
<body>
Hello tartampion
<br>
<a href="index">Home</a>
</body>
</html>"""

class TestServer(threading.Thread):

    def __init__(self,**kw):
        self.kw = kw
        threading.Thread.__init__(self)

    def run(self,**kw):
        Karrigell.run(**self.kw)

class Tester(unittest.TestCase):

    def test_not_found(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            res = urllib.request.urlopen(self.start+"/xyz.azert")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 404)

    def test_echo(self):
        res = urllib.request.urlopen(self.start+"/test.py/hello?name=tartampion")
        self.assertEqual(res.read(),b'Hello tartampion')

    def test_template(self):
        res = urllib.request.urlopen(self.start+"/test.py/bar?name=tartampion")
        info = res.info()
        self.assertIn('Set-Cookie',info)
        cookie = http.cookies.BaseCookie(info['Set-Cookie'])
        self.assertEqual(cookie['role'].value,'tartampion')
        self.assertEqual(cookie['role']['path'],'/')
        self.assertEqual(res.read(),template.encode('ascii'))

    def test_import(self):
        res = urllib.request.urlopen(self.start+"/test.py/import_test")
        self.assertEqual(res.read(),b'<b>foobar</b>')

    def test_file_session(self):
        res = urllib.request.urlopen(self.start+"/test.py/set_session?name=shelley")
        info = res.info()
        self.assertIn('set-cookie',info)
        cookie = info['set-cookie'].split('=')
        self.assertEqual(cookie[0],"session_id")
        session_id = cookie[1]
        req = urllib.request.Request(self.start+"/test.py/get_session")
        req.add_header('Cookie',"=".join(cookie))
        res = urllib.request.urlopen(req)
        self.assertEqual(res.read(),b'shelley')

    def test_memory_session(self):
        res = urllib.request.urlopen(self.start+"/test.py/set_session?name=shelley")
        info = res.info()
        self.assertIn('set-cookie',info)
        cookie = info['set-cookie'].split('=')
        self.assertEqual(cookie[0],"session_id")
        session_id = cookie[1]
        req = urllib.request.Request(self.start+"/test.py/get_session")
        req.add_header('Cookie',"=".join(cookie))
        res = urllib.request.urlopen(req)
        self.assertEqual(res.read(),b'shelley')

    def test_cookie(self):
        res = urllib.request.urlopen(self.start+"/test.py/set_cookie?name=band&val=smiths")
        info = res.info()
        self.assertIn('set-cookie',info)
        cookie = info['set-cookie'].split('=')
        self.assertEqual(cookie[0],"band")
        req = urllib.request.Request(self.start+"/test.py/read_cookie?name=band")
        req.add_header('Cookie',"=".join(cookie))
        res = urllib.request.urlopen(req)
        self.assertEqual(res.read(),b'smiths')


class App1(Karrigell.App):

    hidden = ['.sqlite']
    # test with extra app
    def hide_ext(self,handler):
        for ext in self.hidden:
            if handler.path_info.endswith(ext):
                raise Karrigell.HTTP_ERROR(403)
    filters = [hide_ext]

# test with default app
server = TestServer(port=8082)
server.start()

# test with filtering app
server = TestServer(apps=[App1],port=8083)
server.start()

class Tester1(Tester):
    start = "http://localhost:8082"

class Tester2(Tester):
    start = "http://localhost:8083"

    def test_filter(self):
        # check that files with extension sqlite are forbidden
        with self.assertRaises(urllib.error.HTTPError) as cm:
            res = urllib.request.urlopen(self.start+"/truc.sqlite")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 403)

suite = unittest.TestSuite()
suite1 = unittest.TestLoader().loadTestsFromTestCase(Tester1)
suite2 = unittest.TestLoader().loadTestsFromTestCase(Tester2)

suite.addTests([suite1,suite2])
unittest.TextTestRunner(verbosity=1).run(suite)
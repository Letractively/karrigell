import sys
k_path = r'c:\Karrigell-Python3\20110223_2'
sys.path.insert(0,k_path)

import Karrigell
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

    def run(self):
        Karrigell.run(port=8082)

server = TestServer()
server.start()

class Tester(unittest.TestCase):

    def test_echo(self):
        res = urllib.request.urlopen("http://localhost:8082/test.py/hello?name=tartampion")
        self.assertEqual(res.read(),b'Hello tartampion')

    def test_template(self):
        res = urllib.request.urlopen("http://localhost:8082/test.py/bar?name=tartampion")
        info = res.info()
        self.assertIn('Set-Cookie',info)
        cookie = http.cookies.BaseCookie(info['Set-Cookie'])
        self.assertEqual(cookie['role'].value,'tartampion')
        self.assertEqual(cookie['role']['path'],'/')
        self.assertEqual(res.read(),template.encode('ascii'))

    def test_import(self):
        res = urllib.request.urlopen("http://localhost:8082/test.py/import_test")
        self.assertEqual(res.read(),b'<B>foobar</B>')

    def test_file_session(self):
        res = urllib.request.urlopen("http://localhost:8082/test.py/set_session?name=shelley")
        info = res.info()
        self.assertIn('set-cookie',info)
        cookie = info['set-cookie'].split('=')
        self.assertEqual(cookie[0],"session_id")
        session_id = cookie[1]
        req = urllib.request.Request("http://localhost:8082/test.py/get_session")
        req.add_header('Cookie',"=".join(cookie))
        res = urllib.request.urlopen(req)
        self.assertEqual(res.read(),b'shelley')

    def test_memory_session(self):
        res = urllib.request.urlopen("http://localhost:8082/test.py/set_session?name=shelley")
        info = res.info()
        self.assertIn('set-cookie',info)
        cookie = info['set-cookie'].split('=')
        self.assertEqual(cookie[0],"session_id")
        session_id = cookie[1]
        req = urllib.request.Request("http://localhost:8082/test.py/get_session")
        req.add_header('Cookie',"=".join(cookie))
        res = urllib.request.urlopen(req)
        self.assertEqual(res.read(),b'shelley')

    def test_cookie(self):
        res = urllib.request.urlopen("http://localhost:8082/test.py/set_cookie?name=band&val=smiths")
        info = res.info()
        self.assertIn('set-cookie',info)
        cookie = info['set-cookie'].split('=')
        self.assertEqual(cookie[0],"band")
        req = urllib.request.Request("http://localhost:8082/test.py/read_cookie?name=band")
        req.add_header('Cookie',"=".join(cookie))
        res = urllib.request.urlopen(req)
        self.assertEqual(res.read(),b'smiths')

unittest.main()
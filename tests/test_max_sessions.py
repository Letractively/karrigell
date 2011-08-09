import sys
import os

# modify sys.path to use this version of Karrigell
cwd = os.getcwd()
sys.path.insert(0,os.path.join(os.path.dirname(cwd),'trunk'))

import Karrigell
import Karrigell.sessions

max_sessions = Karrigell.sessions.SQLiteSessionStorage.max_sessions

import threading
import unittest
import urllib.request
import http.cookies

class TestServer(threading.Thread):

    def __init__(self,**kw):
        self.kw = kw
        threading.Thread.__init__(self)

    def run(self,**kw):
        Karrigell.run(**self.kw)

class Tester(unittest.TestCase):

    def test_file_session(self):
        for i in range(200):
            res = urllib.request.urlopen(self.start+"/test.py/set_session?name=shelley")

class App(Karrigell.App):

    session_storage_class = Karrigell.sessions.SQLiteSessionStorage

# test with default app
server = TestServer(port=8082,apps=[App])
server.start()

class Tester1(Tester):
    start = "http://localhost:8082"

suite = unittest.TestSuite()
suite1 = unittest.TestLoader().loadTestsFromTestCase(Tester1)

suite.addTests([suite1])
unittest.TextTestRunner(verbosity=1).run(suite)

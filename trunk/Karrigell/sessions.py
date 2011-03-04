import os
import pickle
import marshal
import traceback
import threading

class SessionElement(dict):

    def __setitem__(self,key,value):
        try:
            marshal.dumps(value)
        except ValueError:
            msg = 'Bad type for session object key %s ' %key
            msg += ': expected built-in type, got %s' %value.__class__
            raise ValueError(msg)
        dict.__setitem__(self,key,value)

class MemorySessionStorage:

    sessions = {}

    def __init__(self,app):
        pass

    def save(self,handler):
        """Save session object as a dictionary"""
        if hasattr(handler,'session_object'):
            self.sessions[handler.session_id] = handler.session_object
    
    def get(self,session_id):
        """Return the session object using self.session_id, or an empty
        SessionElement instance"""
        return self.sessions.get(session_id,SessionElement())

class FileSessionStorage:

    session_dir = None
    # lock for thread-safe session storage
    rlock = threading.RLock()

    def __init__(self,app):
        if self.session_dir is None:
            self.session_dir = os.path.join(app.root_dir,"sessions")
        if not os.path.exists(self.session_dir):
            os.mkdir(self.session_dir)

    def save(self,handler):
        """Save session object as a dictionary"""
        if hasattr(handler,'session_object'):
            self.rlock.acquire() # thread safety
            try:
                session_file = os.path.join(self.session_dir,handler.session_id)
                out = open(session_file,'wb')
                pickle.dump(dict(handler.session_object),out)
                out.close()
            except:
                traceback.print_exc(file=handler.output)
            self.rlock.release()
    
    def get(self,session_id):
        """Return the session object using self.session_id, or an empty
        SessionElement instance"""
        session_file = os.path.join(self.session_dir,session_id)
        try:
            try:
                self.rlock.acquire()
                obj = SessionElement(pickle.load(open(session_file,'rb')))
            except (IOError,AttributeError):
                obj = SessionElement()
                out = open(session_file,'wb')
                pickle.dump({},out)
                out.close()
        finally:
            self.rlock.release()
        return obj


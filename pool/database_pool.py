from infrastructure.mongodb import Client, Session
from models import Model
from module import helper
from threading import Lock
from queue import Queue


class DatabasePool:
    def __init__(self, num_session):
        self.client_pool = dict()
        self.session_pool = dict()
        self.active_session = dict()
        self.lock = Lock()
        for database in Model.get_database_names():
            self.add_client(database=database)
            self.session_pool[database] = dict()
            self.active_session[database] = Queue()
            for _ in range(num_session):
                self.add_session(database=database)

    def add_client(self, database):
        client = Client(database)
        self.lock.acquire()
        self.client_pool.pop(database, None)
        self.client_pool[database] = client
        self.lock.release()

    def get_client(self, database):
        return self.client_pool[database]

    def add_session(self, database):
        exists_session_names = self.session_pool[database].keys()
        session_name = helper.generate_name(prefix=f"{database}_database_session", exist_name=exists_session_names)
        db_session = self.client_pool[database].generate_session()
        session = Session(name=session_name, database=database, session=db_session)
        self.lock.acquire()
        self.session_pool[database][session_name] = session
        self.active_session[database].put(session_name)
        self.lock.release()

    def get_active_session(self, database):
        self.lock.acquire()
        if self.active_session[database].qsize() > 0:
            session_name = self.active_session[database].get()
            self.lock.release()
            return self.session_pool[database][session_name]
        else:
            self.lock.release()
            return None

    def set_active_session(self, session):
        self.lock.acquire()
        self.active_session[session.database].put(session.name)
        self.lock.release()

    def reset_session(self, session):
        self.lock.acquire()
        self.session_pool[session.database].pop(session.name)
        self.lock.release()
        database = session.database
        del session
        self.add_session(database)



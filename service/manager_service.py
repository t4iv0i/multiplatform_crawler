from service.worker_service import Worker
from service.daemon_service import Daemon
from threading import RLock
from module import helper
import random


class Manager:
    def __init__(self, rabbitmq_pool):
        self.index = 0
        self.rabbitmq_pool = rabbitmq_pool
        self.worker_pool = dict(facebook=dict(), instagram=dict(), youtube=dict(), tiktok=dict())
        self.lock = RLock()

    def add_new_worker(self, typ3):
        name = helper.generate_name(prefix=f"{typ3}_worker", exist_name=self.worker_pool[typ3].keys())
        self.index += 1
        worker = Worker(name=name, typ3=typ3, rabbitmq_pool=self.rabbitmq_pool)
        worker.start()
        self.lock.acquire()
        self.worker_pool[typ3][name] = worker
        self.lock.release()

    def get_inactive_worker(self, typ3):
        for name, worker in self.worker_pool[typ3].items():
            if not worker.is_alive():
                return worker
        else:
            return None

    def reset_worker(self, worker):
        typ3 = worker.type
        name = worker.name
        self.lock.acquire()
        worker = self.worker_pool[typ3].pop(name)
        self.lock.release()
        worker.stop()
        del worker
        self.add_new_worker(typ3)

    def add_new_daemon(self):
        self.index += 1
        daemon = Daemon(rabbitmq_pool=self.rabbitmq_pool)
        daemon.start()
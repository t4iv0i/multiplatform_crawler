from service.worker_service import Worker
from threading import Thread, Lock, Event
from module import helper
from time import sleep


class Manager(Thread):
    def __init__(self, rabbitmq_pool, proxy_pool, credential_pool):
        super().__init__()
        self.index = 0
        self.rabbitmq_pool = rabbitmq_pool
        self.proxy_pool = proxy_pool
        self.credential_pool = credential_pool
        self.worker_pool = dict()
        self.lock = Lock()
        self.stop_event = Event()

    def add_new_worker(self):
        name = helper.generate_name(prefix=f"worker", exist_name=self.worker_pool.keys())
        self.index += 1
        worker = Worker(name=name, rabbitmq_pool=self.rabbitmq_pool)
        worker.start()
        self.lock.acquire()
        self.worker_pool[name] = worker
        self.lock.release()

    def get_active_worker(self, typ3):
        for name, worker in self.worker_pool[typ3].items():
            if not worker.is_alive():
                return worker
        else:
            return None

    def reset_worker(self, worker):
        name = worker.name
        self.lock.acquire()
        worker = self.worker_pool.pop(name)
        self.lock.release()
        worker.stop()
        del worker
        self.add_new_worker()

    def stop(self):
        self.stop_event.set()

    def run(self):
        print(f"Manager is started...")
        while True:
            if self.stop_event.is_set():
                print("Manager is stopped!!!")
                break
            sleep(3600)
            self.proxy_pool.save()
            self.credential_pool.save()

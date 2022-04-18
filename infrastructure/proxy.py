from constant import constant
from random import choice
from requests import Session
from module import helper
from threading import Lock


class ProxyPool:
    def __init__(self):
        self.available = list()
        self.active = list()
        self.dead = list()
        self.lock = Lock()
        self.default_ip = self.get_default_ip()
        self.scan()

    @staticmethod
    def get_default_ip():
        session = Session()
        response = session.get(constant.check_ipv4_address)
        ip = response.text
        session.close()
        return ip

    def check_alive(self, proxy):
        session = Session()
        proxy_string = f"https://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
        session.proxies = {'http': proxy_string, 'https': proxy_string}
        try:
            response = session.get(constant.check_ipv4_address)
            ip = response.text
        except Exception as e:
            session.close()
            print(f"Proxy: {proxy} is dead.\nDetail: {str(e)}")
            return False
        else:
            session.close()
            if ip != self.default_ip:
                return True
            else:
                return False

    def get(self):
        self.lock.acquire()
        while len(self.available):
            index = choice(range(len(self.available)))
            proxy = self.available.pop(index)
            if self.check_alive(proxy):
                self.active.append(proxy)
                self.lock.release()
                return proxy
            else:
                self.dead[proxy] = True
        self.lock.release()
        self.scan()
        return None

    def report(self, proxy):
        for index in range(len(self.active)):
            if self.active[index] == proxy:
                self.dead.append(self.active.pop(index))
                break

    def scan(self):
        root_dir = "resources/proxy"
        pattern = r'http://([^\:]+)\:([^\:]+)\@([\.\w]+)\:(\d+)'
        proxies = [zip(["username", "password", "ip", "port"], proxy) for proxy in helper.scan(root_dir=root_dir, pattern=pattern)]
        self.lock.acquire()
        for proxy in self.dead:
            if self.check_alive(proxy):
                proxies.append(proxy)
                self.dead.pop(proxy)
        self.available = dict([(proxy, True) for proxy in proxies])
        self.lock.release()
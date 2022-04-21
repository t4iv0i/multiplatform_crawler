import json
from constant import constant
from os import path
from random import choice
from requests import Session
from module import helper
from threading import Lock


class ProxyPool:
    def __init__(self):
        self.proxies = dict(map(lambda typ3: (typ3, []), constant.type_of_proxy))
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
        proxy_string = f"https://{proxy['username']}:{proxy['password']}@{proxy['hostname']}:{proxy['port']}"
        session.proxies = {'http': proxy_string}
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
        while len(self.proxies["available"]):
            index = choice(range(len(self.proxies["available"])))
            proxy = self.proxies["available"].pop(index)
            if self.check_alive(proxy):
                self.proxies["active"].append(proxy)
                self.lock.release()
                return proxy
            else:
                self.proxies["dead"].append(proxy)
        self.lock.release()
        self.scan()
        return None

    def report(self, proxy):
        is_alive = self.check_alive(proxy)
        self.lock.acquire()
        active = self.proxies["active"]
        for index in range(len(active)):
            if proxy == active[index]:
                self.proxies["active"].pop(index)
                if is_alive:
                    self.proxies["available"].append(proxy)
                else:
                    self.proxies["dead"].append(proxy)
                break
        self.lock.release()

    def scan(self):
        root_dir = path.join("resources", "proxy")
        proxies = helper.scan(root_dir=root_dir, json_type=True)
        self.lock.acquire()
        for proxy in proxies:
            for typ3 in constant.type_of_proxy:
                if proxy in self.proxies[typ3]:
                    break
            else:
                self.proxies["available"].append(proxy)
                print(f"Added proxy: {proxy}")
        self.lock.release()

    def save(self):
        for typ3 in constant.type_of_proxy:
            file_path = path.join("resources", "proxy", "backup", f"{typ3.json}")
            with open(file_path, 'wt') as fp:
                json.dump(self.proxies[typ3], fp)
            print(f"Saved {len(self.proxies[typ3])} {typ3} proxies")


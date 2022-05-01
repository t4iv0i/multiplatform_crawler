from infrastructure.api import Api
from infrastructure.proxy import Proxy
from module import helper
from constant import constant
from os import path
from random import choice
from threading import Lock
import json


class ProxyPool:
    def __init__(self):
        self.proxies = dict()
        for typ3 in constant.type_of_proxy:
            self.proxies[typ3] = dict(map(lambda status: (status, []), constant.status_of_proxy))
        self.lock = Lock()
        self.default_ip = self.get_default_ip()
        print(f"Default ip: {self.default_ip}")
        self.scan()

    @staticmethod
    def get_default_ip():
        api = Api()
        ip = dict()
        for ipv, address in constant.api_check_ip_address.items():
            try:
                response = api.get(url=address, timeout=constant.API_TIMEOUT)
            except:
                api.close()
                ip[ipv] = ""
            else:
                ip[ipv] = response.text
        api.close()
        return ip

    def check(self, proxy):
        ip = proxy.get_ip()
        if ip is None:
            return False
        else:
            for ipv in constant.api_check_ip_address:
                if ip.get(ipv) != "" and ip[ipv] != self.default_ip[ipv]:
                    return True

            print(f"Proxy {proxy} is dead.\nIp: {ip}")
            return False

    def get(self, typ3):
        while True:
            self.lock.acquire()
            if len(self.proxies[typ3]["available"]) > 0:
                index = choice(range(len(self.proxies[typ3]["available"])))
                proxy = self.proxies[typ3]["available"].pop(index)
                self.lock.release()
            else:
                self.lock.release()
                self.update(typ3)
                return None
            if self.check(proxy=proxy):
                self.lock.acquire()
                self.proxies[typ3]["active"].append(proxy)
                self.lock.release()
                return proxy
            else:
                self.lock.acquire()
                self.proxies[typ3]["dead"].append(proxy)
                self.lock.release()

    def set(self, proxy):
        typ3 = proxy.typ3
        for index in range(len(self.proxies[typ3]["active"])):
            _proxy = self.proxies[typ3]["active"][index]
            if proxy.string == _proxy.string:
                self.lock.acquire()
                self.proxies[typ3]["active"].pop(index)
                self.proxies[typ3]["available"].append(proxy)
                self.lock.release()
                break

    def report(self, proxy):
        is_alive = self.check(proxy)
        typ3 = proxy.typ3
        self.lock.acquire()
        active = self.proxies[typ3]["active"]
        for index in range(len(active)):
            if proxy == active[index]:
                self.proxies[typ3]["active"].pop(index)
                if is_alive:
                    self.proxies[typ3]["available"].append(proxy)
                else:
                    self.proxies[typ3]["dead"].append(proxy)
                break
        self.lock.release()
        return is_alive

    def update(self, typ3):
        for index in range(len(self.proxies[typ3]["dead"])):
            proxy = self.proxies[typ3]["dead"][index]
            if self.check(proxy):
                self.lock.acquire()
                self.proxies[typ3]["dead"].pop(index)
                self.proxies[typ3]["available"].append(proxy)
                self.lock.release()

    def scan(self):
        for typ3 in constant.type_of_proxy:
            root_dir = path.join("resources", "proxy", typ3)
            proxies = helper.scan(root_dir=root_dir, json_type=True)
            count = 0
            self.lock.acquire()
            for proxy in proxies:
                proxy_obj = Proxy(**proxy)
                found = False
                for status in constant.status_of_proxy:
                    for current_proxy in self.proxies[typ3][status]:
                        if proxy_obj.string == current_proxy.string:
                            found = True
                            break
                if not found:
                    self.proxies[typ3]["available"].append(proxy_obj)
                    count += 1
            self.lock.release()
            print(f"Added {count} {typ3} proxy")

    def save(self):
        for typ3 in constant.type_of_proxy:
            for status in constant.status_of_proxy:
                file_path = path.join("resources", "proxy", "backup", typ3, f"{status}.json")
                proxies = list(map(lambda proxy: proxy.__dict__, self.proxies[typ3][status]))
                with open(file_path, 'wt') as fp:
                    json.dump(proxies, fp)
                print(f"Saved {len(self.proxies[typ3][status])} {status} {typ3} proxies")


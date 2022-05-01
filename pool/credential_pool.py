from infrastructure import credential as credential_module
from constant import constant
from module import helper
from os import path
from random import choice
from threading import Lock
import json


class CredentialPool:
    def __init__(self, proxy_pool):
        self.available = dict()
        self.backup = dict()
        for domain in constant.url_patterns.keys():
            self.available[domain] = dict(map(lambda typ3: (typ3, []), constant.type_of_credential))
            self.backup[domain] = dict(map(lambda typ3: (typ3, []), constant.type_of_credential))
        self.proxy_pool = proxy_pool
        self.lock = Lock()
        self.scan()

    def set(self, indicators, credential):
        pointer = self
        for indicator in indicators:
            if hasattr(pointer, indicator):
                pointer = getattr(pointer, indicator)
            else:
                pointer = pointer[indicator]
        self.lock.acquire()
        if credential not in pointer:
            pointer.append(credential)
            print(f"Added {credential.typ3}: {credential}")
        self.lock.release()

    def get(self, indicators):
        pointer = self.available
        for indicator in indicators:
            pointer = pointer[indicator]
        self.lock.acquire()
        if len(pointer) > 0:
            index = choice(range(len(pointer)))
            credential = pointer.pop(index)
        else:
            credential = None
        self.lock.release()
        return credential

    def report(self, indicators, credential):
        if credential.typ3 == "token":
            proxy = self.proxy_pool.get(typ3="fast")
        else:
            proxy = self.proxy_pool.get(typ3="resilient")
        if credential.check(proxy=proxy) is False:
            for role in ["available", "backup"]:
                pointer = getattr(self, role)
                for indicator in indicators:
                    pointer = pointer[indicator]
                self.lock.acquire()
                for index in range(len(pointer)):
                    if pointer[index] == credential:
                        pointer.pop(index)
                        print(f"{credential.typ3} {credential} is dead")
                        break
                self.lock.release()
        else:
            pointer = self.available
            for indicator in indicators:
                pointer = pointer[indicator]
            self.lock.acquire()
            pointer.append(credential)
            self.lock.release()
        self.proxy_pool.set(proxy)

    def scan(self):
        for domain in constant.url_patterns.keys():
            for credential_type in constant.type_of_credential:
                root_dir = path.join("resources", domain, credential_type)
                credentials = helper.scan(root_dir=root_dir, json_type=True)
                count = len(self.available[domain][credential_type])
                self.lock.acquire()
                for credential in credentials:
                    for role in ["available", "backup"]:
                        pointer = getattr(self, role)
                        for current_credential in pointer[domain][credential_type]:
                            if credential == current_credential.to_dict():
                                break
                        else:
                            credential_class = getattr(credential_module, credential_type[0].upper()+credential_type[1:])
                            credential_obj = credential_class(**credential)
                            pointer[domain][credential_type].append(credential_obj)
                self.lock.release()
                count = len(self.available[domain][credential_type]) - count
                if count > 0:
                    print(f"Added {count} {domain} {credential_type}")

    def save(self):
        for domain in constant.url_patterns.keys():
            for typ3 in constant.type_of_credential:
                file_path = path.join("resources", domain, "backup", f"{typ3}.json")
                self.lock.acquire()
                credentials = list(map(lambda credential: credential.to_dict(), self.backup[domain][typ3]))
                with open(file_path, 'wt') as fp:
                    json.dump(credentials, fp)
                print(f"Saved {len(self.backup[domain][typ3])} {domain} {typ3}")
                self.lock.release()

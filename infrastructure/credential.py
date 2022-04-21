from constant import constant
from module import helper
from os import path
from random import choice
from threading import Lock
import json


class CredentialPool:
    def __init__(self):
        credential = dict(map(lambda typ3: (typ3, []), constant.type_of_credential))
        self.credentials = dict(map(lambda domain: (domain, credential.copy()), constant.url_patterns.keys()))
        self.lock = Lock()

    def check_alive(self):
        pass

    def set(self, indicators, credential):
        pointer = self.credentials
        for indicator in indicators:
            pointer = pointer[indicator]
        self.lock.acquire()
        if credential not in pointer:
            pointer.append(credential)
            print(f"Added {' '.join(indicators)}: {credential}")
        self.lock.release()

    def get(self, indicators):
        pointer = self.credentials
        for indicator in indicators:
            pointer = pointer[indicator]
        self.lock.acquire()
        if len(pointer) > 0:
            credential = choice(pointer)
        else:
            credential = None
        self.lock.release()
        return credential

    def report(self, indicators, credential):
        pointer = self.credentials
        for indicator in indicators:
            pointer = pointer[indicator]
        self.lock.acquire()
        for index in range(len(pointer)):
            if pointer[index] == credential:
                pointer.pop(index)
                print(f"{' '.join(indicators)} {credential} is dead")
                break
        self.lock.release()

    def scan(self):
        for domain in constant.url_patterns.keys():
            for typ3 in constant.type_of_credential:
                root_dir = path.join("resources", domain, typ3)
                credendials = helper.scan(root_dir=root_dir, json_type=True)
                self.lock.acquire()
                for credendial in credendials:
                    if credendial not in self.credentials[domain][typ3]:
                        self.credentials[domain][typ3].append(credendial)
                        print(f"Added {domain}.{typ3}: {credendial}")
                self.lock.release()

    def save(self):
        for domain in constant.url_patterns.keys():
            for typ3 in constant.type_of_credential:
                file_path = path.join("resources", domain, "backup", f"{typ3}.json")
                self.lock.acquire()
                with open(file_path, 'wt') as fp:
                    json.dump(self.credentials[domain][typ3], fp)
                print(f"Saved {len(self.credentials[domain][typ3])} {domain} {typ3}")
                self.lock.release()

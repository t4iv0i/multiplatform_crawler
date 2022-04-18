from module import helper
from os import path
from random import choice
from threading import Lock


class CredentialPool:
    def __init__(self):
        self.credentials = {
            "facebook": {"account": [], "access_token": [], "cookie": []},
            "instagram": {"account": [], "access_token": [], "cookie": []},
            "youtube": {"account": [], "access_token": [], "cookie": []}
        }
        self.lock = Lock()

    def check_alive(self):
        pass

    def set(self, indicators, credential):
        pointer = self.credentials
        for indicator in indicators:
            pointer = pointer[indicator]
        self.lock.acquire()
        pointer.append(credential)
        self.lock.release()

    def get(self, indicators):
        pointer = self.credentials
        for indicator in indicators:
            pointer = pointer[indicator]
        credential = choice(pointer)
        return credential

    def report(self, indicators, credential):
        pointer = self.credentials
        self.lock.acquire()
        for indicator in indicators:
            pointer = pointer[indicator]
        for index in range(len(pointer)):
            if pointer[index] == credential:
                pointer.pop(index)
                break
        self.lock.release()

    def scan(self, indicators):
        root_dir = path.join("resources", *indicators)
        pointer = self.credentials
        for indicator in indicators:
            pointer = pointer[indicator]
        if indicators[-1] == "access_token":
            pointer += helper.scan(root_dir=root_dir, pattern=r"\w{150,250}")
        else:
            pointer += helper.scan(root_dir=root_dir, json_type=True)
        
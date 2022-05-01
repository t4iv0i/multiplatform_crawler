from requests import Session
from requests.cookies import create_cookie
from os import listdir
from os.path import join, isdir
import json
import re
from bs4 import BeautifulSoup
from threading import Thread, Lock
from queue import Queue
from time import sleep

num_of_worker = 11
proxies = {"http": "http://user-kocstaging:EV!L&D!hJ6Ugy5Rs@vn.smartproxy.com:46000"}
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "vi-VN, en-US",
    "Cache-Control": "private, no-cache, no-store, must-revalidate",
    "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36",
    "Connection": "keep alive"
}


def check_cookie(cookies):
    session = Session()
    session.proxies = proxies
    session.headers = headers
    for name, value in cookies.items():
        cookie_obj = create_cookie(domain=".facebook.com", name=name, value=value)
        session.cookies.set_cookie(cookie=cookie_obj)
    try:
        response = session.get(url=f"https://m.facebook.com")
        message = response.json()
    except Exception as e:
        return None, {"status": "connection error", "message": str(e)}
    else:
        if response.status_code != 200:
            return None, {"status": "error", "code": message["error"]["code"], "subcode": message["error"].get("error_subcode")}
        set_cookie = response.headers.get("Set-Cookie")
        if set_cookie:
            regex = re.findall(r'\s*([^=]+)\s*=\s*([^;]+)\s*;*', set_cookie)
            new_cookies = dict(regex)
            for name in ["c_user", "spin", "useragent"]:
                if new_cookies.get(name) and new_cookies[name] == "deleted":
                    return None, {"status": "dead"}
            else:
                for name in ["c_user", "xs", "datr", "useragent"]:
                    if new_cookies.get(name):
                        cookies[name] = new_cookies[name]
                return cookies, {"status": "update"}
        else:
            return cookies, {"status": "live"}


def check_access_token(access_token):
    session = Session()
    session.proxies = proxies
    session.headers = headers
    try:
        response = session.get(url=f"https://graph.facebook.com/v12.0/me?access_token={access_token}")
        message = response.json()
    except Exception as e:
        return None, {"status": "connection error", "message": str(e)}
    else:
        if response.status_code != 200:
            return access_token, {"status": "error", "code": message["error"]["code"], "subcode": message["error"].get("error_subcode")}
        return access_token, {"status": "live"}


def verify_cookies(cookies):
    session = Session()
    session.proxies = proxies
    session.headers = headers
    for name, value in cookies.items():
        cookie_obj = create_cookie(domain=".facebook.com", name=name, value=value)
        session.cookies.set_cookie(cookie=cookie_obj)
    try:
        response = session.get(url=f"https://mbasic.facebook.com/baaukrysie")
        if response.status_code != 200:
            raise Exception(f"{response.status_code}")
    except Exception as e:
        return None, {"status": "connection error"}
    else:
        set_cookie, status = response.headers.get("Set-Cookie"), None
        if set_cookie:
            regex = re.findall(r'\s*([^=]+)\s*=\s*([^;]+)\s*;*', set_cookie)
            new_cookies = dict(regex)
            for name in ["c_user", "spin", "xs", "datr", "useragent"]:
                if new_cookies.get(name):
                    if new_cookies[name] == "deleted":
                        status = "delete"
                        cookies.pop(name)
                    else:
                        cookies[name] = new_cookies[name]
                        status = "update"
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        for element in links:
            try:
                href = element["href"]
            except:
                # print(element)
                continue
            uid = re.findall(r'[\?\&]id=(\d+)', href)
            if uid and uid[0] == "100043317711494":
                if status is not None:
                    return cookies, {"status": status}
                else:
                    return cookies, {"status": "live"}
        return None, {"status": "dead"}


def get_file_path(root_dir):
    result = list()
    for file_name in listdir(root_dir):
        file_path = join(root_dir, file_name)
        if isdir(file_path):
            continue
        result.append(file_path)
    return result


def save(elements, file_path):
    with open(file_path, 'wt') as fp:
        for element in elements:
            fp.write(element + '\n')


class Worker(Thread):
    def __init__(self, function, input_queue, result_queue):
        super().__init__()
        self.function = function
        self.input_queue = input_queue
        self.result_queue = result_queue
        self.lock = Lock()

    def run(self):
        while True:
            self.lock.acquire()
            if self.input_queue.qsize() > 0:
                message = self.input_queue.get()
                self.lock.release()
            else:
                self.lock.release()
                sleep(3)
                continue
            if message == "break":
                self.result_queue.put("break")
                print("worker done")
                break
            result = self.function(message)
            self.lock.acquire()
            self.result_queue.put(result)
            self.lock.release()


class Saver(Thread):
    def __init__(self, file_name, result_queue):
        super().__init__()
        self.file_pointer = open(file_name, 'wt')
        self.result_queue = result_queue
        self.lock = Lock()
        self.count = 0

    def run(self):
        while True:
            messages = list()
            self.lock.acquire()
            size = self.result_queue.qsize()
            if size:
                for count in range(size):
                    messages.append(self.result_queue.get())
                self.lock.release()
            else:
                self.lock.release()
                sleep(3)
                continue
            for message in messages:
                if type(message) == tuple:
                    element, status = message
                    if status["status"] == "live":
                        if type(element) == dict:
                            string = json.dumps(element)
                            self.file_pointer.write(string+',\n')
                        elif type(element) == str:
                            self.file_pointer.write(element + '\n')
                elif message == "break":
                    self.count += 1
                    if self.count == num_of_worker:
                        self.file_pointer.close()
                        print("Saver done...")
                        return


if __name__ == "__main__":
    input_queue, result_queue = Queue(), Queue()
    root_dir = 'resources/facebook'
    account_root_dir = join(root_dir, "accounts")
    access_token_root_dir = join(root_dir, 'access_tokens')
    cookie_root_dir = join(root_dir, 'cookies')
    live_accounts, error_accounts, dead_accounts, unknown_accounts = dict(), dict(), dict(), dict()
    known_elements, live_cookies, live_access_tokens = dict(), list(), list()
    file_paths = get_file_path(root_dir)
    file_paths += get_file_path(account_root_dir)
    file_paths += get_file_path(access_token_root_dir)
    for count in range(num_of_worker):
        worker = Worker(function=check_access_token, input_queue=input_queue, result_queue=result_queue)
        worker.start()
    saver = Saver(file_name=join(access_token_root_dir, 'live'), result_queue=result_queue)
    saver.start()
    for file_path in file_paths:
        with open(file_path, 'rt') as fp:
            for line in fp:
                account = line.strip()
                unknown_accounts[account] = True
                for element in line.split('|'):
                    element = element.strip()
                    if known_elements.get(element):
                        continue
                    known_elements[element] = True

                    # regex = re.findall(r'\s*([^=]+)\s*=\s*([^;]+)\s*;*', element)
                    # if regex and len(regex) > 2:
                    #     origin_cookie = dict(regex)
                    #     input_queue.put(origin_cookie)
                        # status = check_cookie(origin_cookie
                        # if status is None:
                        #     status = check_cookie(origin_cookie)
                        # if not status:
                        #     dead_accounts[account] = True
                        #     live_accounts.pop(account, None)
                        #     print(f"Dead cookies: {origin_cookie}")
                        # elif message["status"] == "error":
                        #     if error_accounts.get(account):
                        #         error_accounts[account].update(message)
                        #     else:
                        #         error_accounts[account] = message
                        #     print(f"Error cookies: {message['code']}-{message['subcode']}-{cookie}")
                        # elif message["status"] in ["live", "update"]:
                        # else:
                        #     live_accounts[account] = True
                        #     dead_accounts.pop(account, None)
                        #     live_cookies.append(origin_cookie)
                        #     print(f"Live cookies: {origin_cookie}")
                        # unknown_accounts.pop(account, None)
                        # continue

                    regex = re.findall(r'^\w{150,250}$', element)
                    if regex:
                        input_queue.put(regex[0])

                        # access_token, message = check_access_token(regex[0])
                        # if message["status"] == "connection error":
                        #     access_token, message = check_access_token(regex[0])
                        # if message["status"] == "dead":
                        #     dead_accounts[account] = True
                        #     live_accounts.pop(account, None)
                        #     print(f"Dead access_token: {regex[0]}")
                        # elif message["status"] == "error":
                        #     if error_accounts.get(account):
                        #         error_accounts[account].update(message)
                        #     else:
                        #         error_accounts[account] = message
                        #     print(f"Error access token: {message['code']}-{message['subcode']}-{access_token}")
                        # elif message["status"] == "live":
                        #     live_accounts[account] = True
                        #     dead_accounts.pop(account, None)
                        #     live_access_tokens.append(access_token)
                        #     print(f"Live access token: {access_token}")
                    #     unknown_accounts.pop(account, None)
    for count in range(num_of_worker):
        input_queue.put("break")
        
    # with open(join(access_token_root_dir, 'live_access_tokens'), 'wt') as save_access_tokens:
    #     for access_token in live_access_tokens:
    #         save_access_tokens.write(access_token + '\n')
    # with open(join(cookie_root_dir, 'live.json'), 'wt') as fp:
    #     json.dump(live_cookies, fp)
    # save(live_accounts, join(access_token_root_dir, 'live_accounts'))
    # with open(join(account_root_dir, 'error_accounts'), 'wt') as fp:
    #     for account, message in error_accounts.items():
    #         fp.write(f"{account}|code={message['code']}|subcode={message['subcode']}\n")
    # save(dead_accounts, join(account_root_dir, 'dead_accounts'))
    # save(unknown_accounts, join(account_root_dir, 'unknown_accounts'))



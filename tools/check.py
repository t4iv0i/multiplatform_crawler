from infrastructure.simulator import init_chrome
from threading import Thread, RLock
from queue import Queue
from time import sleep
from pyvirtualdisplay import Display


display = Display(visible=False, size=(1920, 1080))
display.start()


def check(queue, save):
    lock = RLock()
    while True:
        if queue.qsize() == 0:
            break
        else:
            try:
                lock.acquire()
                proxy_credential, instagram_credential = queue.get(0.1)
            except:
                lock.release()
                break
            else:
                lock.release()
                browser = init_chrome('instagram', proxy_credential=proxy_credential, instagram_credential=instagram_credential)
                if browser is None:
                    lock.acquire()
                    save.put(('dead', instagram_credential))
                    lock.release()
                else:
                    lock.acquire()
                    save.put(('live', instagram_credential))
                    lock.release()
                    browser.close()


def write(queue):
    lock = RLock()
    count = 0
    while True:
        if count == 100:
            break
        if queue.qsize() > 0:
            live = open("resources/instagram/live_accounts", 'at')
            dead = open("resources/instagram/dead_accounts", "at")
            for _ in range(queue.qsize()):
                lock.acquire()
                status, instagram_credential = queue.get()
                lock.release()
                if status == 'live':
                    live.write(instagram_credential + '\n')
                else:
                    dead.write(instagram_credential + '\n')
                count += 1
            live.close()
            dead.close()
        else:
            sleep(10)


proxy_credentials, facebook_credentials, instagram_credentials = list(), list(), list()
with open('resources/proxy/smart_proxy', 'rt') as fp:
    for line in fp:
        proxy_credentials.append(line.strip())
# with open("resources/facebook/accounts", 'rt') as fp:
#     for line in fp:
#         facebook_credentials.append(line.strip())
with open("resources/instagram/account_backup", 'rt') as fp:
    for line in fp:
        instagram_credentials.append(line.strip())

get, save = Queue(), Queue()
for index in range(100):
    proxy_credential, instagram_credential = proxy_credentials[index], instagram_credentials[index]
    get.put((proxy_credential, instagram_credential))

for count in range(10):
    checker = Thread(target=check, args=(get, save))
    checker.start()

writer = Thread(target=write, args=(save,))
writer.start()
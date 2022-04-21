from infrastructure import rabbitmq, mongodb, proxy, credential, api, browser
from constant import constant
import config
import json
from pyvirtualdisplay import Display

# display = Display(visible=False, size=(1920, 1080))
# display.start()

rabbitmq_pool = rabbitmq.RabbitPool()
database_pool = mongodb.DatabasePool(num_session=constant.NUM_OF_WORKERS)
proxy_pool = proxy.ProxyPool()
proxy_pool.scan()
credential_pool = credential.CredentialPool()
credential_pool.scan()
browser_pool = browser.BrowserPool(proxy_pool=proxy_pool, credential_pool=credential_pool)
for i in range(constant.NUM_OF_WORKERS):
    browser_pool.add(typ3="proxy")
for i in range(constant.NUM_OF_WORKERS//2):
    browser_pool.add(typ3="normal")
api_pool = api.ApiPool(proxy_pool=proxy_pool, credential_pool=credential_pool, browser_pool=browser_pool)
for i in range(constant.NUM_OF_WORKERS):
    api_pool.add(typ3="normal")
for i in range(constant.NUM_OF_WORKERS):
    api_pool.add(typ3="cookie")

from service.manager_service import Manager

manager = Manager(rabbitmq_pool=rabbitmq_pool, proxy_pool=proxy_pool, credential_pool=credential_pool)
for i in range(constant.NUM_OF_WORKERS):
    manager.add_new_worker()
manager.start()
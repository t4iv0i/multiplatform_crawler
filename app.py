from pool.rabbitmq_pool import RabbitMQPool
from pool.database_pool import DatabasePool
from pool.proxy_pool import ProxyPool
from pool.credential_pool import CredentialPool
from pool.api_pool import ApiPool
from pool.browser_pool import BrowserPool
from constant import constant
from pyvirtualdisplay import Display

# display = Display(visible=False, size=(1920, 1080))
# display.start()

rabbitmq_pool = RabbitMQPool()
database_pool = DatabasePool(num_session=constant.NUM_OF_WORKERS)
proxy_pool = ProxyPool()
credential_pool = CredentialPool(proxy_pool=proxy_pool)
browser_pool = BrowserPool(proxy_pool=proxy_pool, credential_pool=credential_pool)
for i in range(constant.NUM_OF_WORKERS):
    browser_pool.add(typ3="proxy")
for i in range(constant.NUM_OF_WORKERS):
    browser_pool.add(typ3="normal")
api_pool = ApiPool(proxy_pool=proxy_pool, credential_pool=credential_pool, browser_pool=browser_pool)
for i in range(constant.NUM_OF_WORKERS):
    api_pool.add(typ3="normal")
for i in range(constant.NUM_OF_WORKERS):
    api_pool.add(typ3="cookie")

from service.manager_service import Manager

manager = Manager(rabbitmq_pool=rabbitmq_pool, proxy_pool=proxy_pool, credential_pool=credential_pool)
for i in range(constant.NUM_OF_WORKERS):
    manager.add_new_worker()
manager.start()

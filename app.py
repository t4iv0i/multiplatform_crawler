from infrastructure import rabbitmq, mongodb, api, browser
from constant import constant
import config
import json
from pyvirtualdisplay import Display

# display = Display(visible=False, size=(1920, 1080))
# display.start()

rabbitmq_pool = rabbitmq.RabbitPool()
proxies, facebook_tokens, instagram_tokens = list(), list(), list()
with open('resources/proxy/smart_proxy', 'rt') as fp:
    for line in fp:
        proxies.append(line.strip())

with open("resources/facebook/access_token/live", 'rt') as fp:
    for line in fp:
        facebook_tokens.append(line.strip())

with open("resources/instagram/accounts/live", 'rt') as fp:
    for line in fp:
        instagram_tokens.append(line.strip())

youtube_tokens = list()
api_pool = api.ApiPool(facebook_tokens=facebook_tokens, instagram_tokens=instagram_tokens, youtube_tokens=youtube_tokens,
                       proxies=proxies)
for i in range(constant.NUM_OF_API_CRAWLERS):
    api_pool.add_new_api()
browser_pool = browser.BrowserPool(proxies=proxies)
database_pool = mongodb.DatabasePool(num_session=constant.NUM_OF_DB_SESSION)

from service.manager_service import Manager

manager = Manager(rabbitmq_pool=rabbitmq_pool)

for i in range(constant.NUM_OF_FACEBOOK_CRAWLERS):
    manager.add_new_worker(typ3='facebook')

for i in range(constant.NUM_OF_INSTAGRAM_CRAWLERS):
    manager.add_new_worker(typ3='instagram')

# for i in range(constant.NUM_OF_TIKTOK_CRAWLERS):
#     manager.add_new_worker(typ3='tiktok')
#
# for i in range(constant.NUM_OF_YOUTUBE_CRAWLERS):
#     manager.add_new_worker(typ3='youtube')

for i in range(constant.NUM_OF_DAEMONS_CRAWLERS):
    manager.add_new_daemon()
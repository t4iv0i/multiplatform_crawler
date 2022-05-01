from infrastructure.browser import Browser
from infrastructure.proxy import Proxy
from infrastructure.credential import Account
import json
import random


with open("/home/t4iv0i/PycharmProjects/multiplatform_crawler/resources/proxy/fast/vietproxy_http.json", "rt") as fp:
    proxies = json.load(fp)

with open("/home/t4iv0i/PycharmProjects/multiplatform_crawler/resources/facebook/account/account.json", "rt") as fp:
    accounts = json.load(fp)

for account in accounts[3:]:
    account = {"facebook": Account(**account)}
    proxy = Proxy(**random.choice(proxies))
    browser = Browser(proxy=proxy, account=account)
    browser.generate_cookie(domain="facebook")
    _ = input()
    browser.browser.close()
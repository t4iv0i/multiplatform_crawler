from requests import Session
import json

with open("resources/proxy/fast/proxygiare_http.json", "rt") as fp:
    proxies = json.load(fp)
for proxy in proxies:
    session = Session()
    session.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "vi-VN, en-US",
            "Cache-Control": "private, no-cache, no-store",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Connection": "keep alive"
        }
    # {proxy["username"]}:{proxy["password"]}@
    session.proxies = {
        'http': f'{proxy["scheme"]}://{proxy["username"]}:{proxy["password"]}@{proxy["hostname"]}:{proxy["port"]}',
        'https': f'{proxy["scheme"]}://{proxy["username"]}:{proxy["password"]}@{proxy["hostname"]}:{proxy["port"]}'
    }
    print(proxy)
    for site in [
                 "https://api.ipify.org",
                 "https://api6.ipify.org/",
                 # "https://mbasic.facebook.com/",
                 # "https://www.instagram.com/"
        ]:
        try:
            r = session.get(site, timeout=7)
        except Exception as e:
            print(f"Detail: {str(e)}")
        else:
            print(r.text)
            print(r.status_code)
            # print(r.reason)
    session.close()
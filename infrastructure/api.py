from requests import Session
from requests.cookies import create_cookie
from threading import Lock
from module import helper
import re


class Api(Session):
    def __init__(self, name, typ3, proxy=None, token=None, cookie=None):
        super().__init__()
        self.name = name
        self.typ3 = typ3
        self.headers.update({
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "vi-VN, en-US",
            "Cache-Control": "private, no-cache, no-store",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Connection": "keep alive"
        })
        if proxy:
            self.proxy = proxy
            self.proxy_string = f"https://{proxy['username']}:{proxy['password']}@{proxy['hostname']}:{proxy['port']}"
        if token:
            self.token = token
        if cookie:
            self.cookie = cookie
            cookie_obj = dict()
            for domain in cookie:
                cookie_obj[domain] = list()
                for name, value in cookie[typ3]:
                    obj = create_cookie(domain=f".{domain}.com", name=name, value=value)
                    cookie_obj[typ3].append(obj)
            self.cookie_obj = cookie_obj

    def set_cookie(self, typ3):
        for cookie_obj in self.cookie_obj[typ3]:
            self.cookies.set_cookie(cookie_obj)

    # @staticmethod
    # def parse_cookies(raw_cookies):
    #     regex = re.findall(r'\s*([^=]+)\s*=\s*([^;]+)\s*;*', raw_cookies)
    #     return dict(regex)
    #
    # def update_cookies(self, typ3, raw_cookies):
    #     new_cookies = self.parse_cookies(raw_cookies=raw_cookies)
    #     if typ3 == "facebook":
    #         for name in ["c_user", "spin", "useragent"]:
    #             if new_cookies.get(name) and new_cookies[name] == "deleted":
    #                 return False
    #         for name in ["c_user", "xs", "datr", "useragent"]:
    #             if new_cookies.get(name):
    #                 cookie_obj = create_cookie(domain=f".{typ3}.com", name=name, value=new_cookies[name])
    #                 self.cookies.update(cookie_obj)
    #         return True
    #     elif typ3 == "instagram":
    #         pass


class ApiPool:
    def __init__(self, proxy_pool, credential_pool, browser_pool):
        self.proxy_pool = proxy_pool
        self.credential_pool = credential_pool
        self.browser_pool = browser_pool
        self.pool = {"normal": {}, "cookie": {}}
        self.active = {"normal": [], "cookie": []}
        self.lock = Lock()

    def add(self, typ3):
        proxy = self.proxy_pool.get()
        if proxy is None:
            print(f"Cant add new api, no available proxy.")
            return None
        token, cookie = dict(), dict()
        for domain in ["facebook"]:
            access_token, error = self.browser_pool.generate_token(typ3=domain)
            if error is not None:
                print(error)
                return None
            else:
                token[domain] = access_token
                self.credential_pool.set([domain, "token"], access_token)
            if typ3 == "cookie":
                cookie[domain] = self.credential_pool.get(indicators=[domain, "cookie"])
        self.lock.release()
        name = helper.generate_name(prefix=f"api", exist_name=self.pool.keys())
        api = Api(name=name, typ3=typ3, proxy=proxy, token=token, cookie=cookie)
        self.lock.acquire()
        self.pool[typ3][name] = api
        self.active[typ3].append(name)
        self.lock.release()

    def get_active(self, typ3):
        self.lock.acquire()
        if len(self.active) > 0:
            name = self.active[typ3].pop(0)
            self.lock.release()
            api = self.pool[typ3][name]
            return api, None
        else:
            self.lock.release()
            return None, {"message": "No available api", "status_code": 400}

    def set_active(self, api):
        api.proxies = {}
        api.cookies.clear()
        self.lock.acquire()
        self.active[api.typ3].append(api.name)
        self.lock.release()

    def reset(self, api, typ3, reason):
        print(f"{api.name} is dead. Reason: {typ3}/{reason}.\nResetting...")
        self.lock.acquire()
        self.pool.pop(api.name)
        self.lock.release()
        proxy = api.proxy
        self.proxy_pool.report(proxy)
        for domain in ["facebook", "instagram", "tiktok", "youtube"]:
            for credential_type in ["token", "cookie"]:
                try:
                    credential_obj = getattr(api, credential_type)
                except:
                    continue
                else:
                    credential = credential_obj.get(domain)
                    if credential:
                        if domain == typ3 and credential_type == reason:
                            self.credential_pool.report(indicators=[typ3, reason], credential=credential)
                        else:
                            self.credential_pool.set(indicators=[domain, credential_type], credential=credential)
        self.add(typ3=api.typ3)
        api.close()
        del api

    def request(self, url, typ3, method, **kwargs):
        if kwargs.get("cookie"):
            api, error = self.get_active(typ3="cookie")
            api.set_cookie(typ3)
        else:
            api, error = self.get_active(typ3="normal")
        if error is not None:
            return None, error
        kw = dict()
        if method == "GET":
            kw["params"] = kwargs.get("params")
        elif method == "POST":
            kw["data"] = kwargs.get("data")
        if kwargs.get("token"):
            if "access_token" not in url:
                kw["access_token"] = api.token[typ3]
        if kwargs.get("proxy"):
            api.proxies = {"http": api.proxy_string}
        print(url)
        print(kw)
        try:
            response = api.request(method=method, url=url, **kw)
        except Exception as e:
            if kwargs.get("proxy"):
                self.reset(api=api, typ3=typ3, reason="proxy")
            else:
                self.reset(api=api, typ3=typ3, reason="abnormal")
            return None, {"message": f"Request error: {str(e)}", "status_code": 400}
        else:
            if "json" in response.headers["Content-Type"]:
                try:
                    data = response.json()
                except Exception as e:
                    return None, {"message": f"Cant {method} {url}. \nDetail: {str(e)}"}
                if data.get("error"):
                    self.reset(api=api, typ3=typ3, reason="access_token")
                    return data, {"message": data["error"], "status_code": 400}
                self.set_active(api)
                return data, None
            elif "html" in response.headers["Content-Type"]:
                if response.status_code != 200:
                    self.set_active(api)
                    return None, {"message": f"Cant {method} {url}.\nStatus code: {response.status_code}", "status_code": 400}
                data = response.text
                # set_cookie = response.headers.get("Set-Cookie")
                # if set_cookie:
                #     status = api.update_cookies(typ3=typ3, raw_cookies=set_cookie)
                #     if not status:
                #         self.reset(api=api, typ3=typ3, reason="cookie")
                self.set_active(api)
                return data, None

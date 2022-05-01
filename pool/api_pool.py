from infrastructure.api import Api
from module import helper
from constant import constant
from threading import Lock


class ApiPool:
    def __init__(self, proxy_pool, credential_pool, browser_pool):
        self.proxy_pool = proxy_pool
        self.credential_pool = credential_pool
        self.browser_pool = browser_pool
        self.pool = {"normal": {}, "cookie": {}}
        self.active = {"normal": [], "cookie": []}
        self.lock = Lock()

    def add(self, typ3):
        proxy = self.proxy_pool.get(typ3="fast")
        if proxy is None:
            print(f"Cant add new api, no available proxy.")
            return None
        token, cookie = dict(), None
        for domain in ["facebook"]:
            token_obj = self.credential_pool.get(indicators=[domain, "token"])
            if token_obj is None:
                browser = self.browser_pool.get(typ3="proxy")
                if browser is None:
                    print(f"Can't add new api, no available browser.")
                    self.proxy_pool.set(proxy)
                    return self.add(typ3=typ3)
                token_obj, error = browser.generate_token(typ3=domain)
                if error is not None:
                    print(error)
                    self.browser_pool.reset(browser=browser, domain=domain, reason="cookie")
                    return self.add(typ3=typ3)
                else:
                    self.credential_pool.set(indicators=["backup", domain, "token"], credential=token_obj)
                    self.browser_pool.set(browser)
                token[domain] = token_obj
        if typ3 == "cookie":
            cookie = dict()
            for domain in ["facebook", "instagram"]:
                _cookie = self.credential_pool.get(indicators=[domain, "cookie"])
                if _cookie is None:
                    browser = self.browser_pool.get(typ3="proxy")
                    if browser is None:
                        self.proxy_pool.set(proxy)
                        return self.add(typ3=typ3)
                    _cookie, error = browser.generate_cookie(domain=domain)
                    if error is not None:
                        print(error)
                        self.browser_pool.reset(browser=browser, domain=domain, reason="account")
                        return self.add(typ3=typ3)
                    else:
                        self.credential_pool.set(indicators=["available", domain, "cookie"], credential=_cookie)
                        self.credential_pool.set(indicators=["backup", domain, "cookie"], credential=_cookie)
                        self.browser_pool.set(browser)
                cookie[domain] = _cookie
        name = helper.generate_name(prefix=f"{typ3}_api", exist_name=self.pool[typ3].keys())
        api = Api(name=name, typ3=typ3, proxy=proxy, token=token, cookie=cookie)
        self.lock.acquire()
        self.pool[typ3][name] = api
        self.active[typ3].append(name)
        self.lock.release()

    def get_active(self, typ3):
        self.lock.acquire()
        if len(self.active[typ3]) > 0:
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

    def reset(self, api, domain, reason):
        print(f"{api.name} is dead. Reason: {domain}/{reason}.\nResetting...")
        self.lock.acquire()
        self.pool[api.typ3].pop(api.name)
        self.lock.release()
        self.proxy_pool.report(api.proxy)
        for _domain in ["facebook", "instagram", "tiktok", "youtube"]:
            for credential_type in ["token", "cookie"]:
                try:
                    credential_obj = getattr(api, credential_type)
                except:
                    continue
                else:
                    credential = credential_obj.get(_domain)
                    if credential:
                        if _domain == domain and credential_type == reason:
                            self.credential_pool.report(indicators=[domain, reason], credential=credential)
                        else:
                            self.credential_pool.set(indicators=[_domain, credential_type], credential=credential)
        self.add(typ3=api.typ3)
        api.close()
        del api

    def request(self, url, domain, method, **kwargs):
        if kwargs.get("cookie"):
            api, error = self.get_active(typ3="cookie")
            if error is not None:
                return None, error
            api.set_cookie(domain)
        else:
            api, error = self.get_active(typ3="normal")
            if error is not None:
                return None, error
        kw = dict()
        if method == "GET":
            kw["params"] = kwargs.get("params", {})
            if kwargs.get("token"):
                if "access_token" not in url:
                    kw["params"]["access_token"] = api.token[domain]
        elif method == "POST":
            kw["data"] = kwargs.get("data", {})
        if kwargs.get("proxy"):
            api.proxies = {"http": api.proxy.string, "https": api.proxy.string}
        print(url)
        print(kw)
        try:
            response = api.request(method=method, url=url, **kw, timeout=constant.API_TIMEOUT)
        except Exception as e:
            if kwargs.get("cookie"):
                self.reset(api=api, domain=domain, reason="cookie")
            elif kwargs.get("token"):
                self.reset(api=api, domain=domain, reason="token")
            return None, {"message": f"Request error: {str(e)}", "status_code": 400}
        else:
            if "json" in response.headers["Content-Type"]:
                try:
                    data = response.json()
                except Exception as e:
                    self.set_active(api)
                    return None, {"message": f"Cant {method} {url}. \nDetail: {str(e)}"}
                if domain == "facebook" and data.get("error"):
                    self.reset(api=api, domain=domain, reason="token")
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

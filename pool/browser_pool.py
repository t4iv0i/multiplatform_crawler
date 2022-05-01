from infrastructure.browser import Browser
from module import helper
from threading import Lock


class BrowserPool:
    def __init__(self, proxy_pool, credential_pool):
        self.proxy_pool = proxy_pool
        self.credential_pool = credential_pool
        self.pool = {"proxy": {}, "normal": {}}
        self.active = {"proxy": [], "normal": []}
        self.lock = Lock()

    def add(self, typ3):
        name = helper.generate_name(prefix=f"{typ3}_browser", exist_name=self.pool[typ3].keys())
        if typ3 == "proxy":
            proxy = self.proxy_pool.get(typ3="resilient")
            if proxy is None:
                print(f"Can't create new {typ3} browser. No available proxy")
                return None
            account = dict()
            for domain in ["facebook", "instagram"]:
                _account = self.credential_pool.get(indicators=[domain, "account"])
                if _account is None:
                    print(f"Can't create new {typ3} browser. No available account")
                    self.proxy_pool.set(proxy)
                    return None
                account[domain] = _account
            browser = Browser(name=name, proxy=proxy, account=account)
            for domain in ["facebook", "instagram"]:
                cookie, error = browser.generate_cookie(domain=domain)
                if error is not None:
                    browser.browser.close()
                    proxy_status = self.proxy_pool.report(proxy)
                    if proxy_status:
                        self.credential_pool.report(indicators=[domain, "account"], credential=account[domain])
                    else:
                        self.credential_pool.set(indicators=["available", domain, "account"], credential=account[domain])
                    return self.add(typ3=typ3)
                else:
                    self.credential_pool.set(indicators=["available", domain, "cookie"], credential=cookie)
                    self.credential_pool.set(indicators=["backup", domain, "cookie"], credential=cookie)
                    self.credential_pool.set(indicators=["available", domain, "account"], credential=account[domain])
        else:
            browser = Browser(name=name)
        self.lock.acquire()
        self.pool[typ3][name] = browser
        self.active[typ3].append(name)
        self.lock.release()

    def get(self, typ3):
        self.lock.acquire()
        if len(self.active[typ3]) > 0:
            name = self.active[typ3].pop(0)
            self.lock.release()
            return self.pool[typ3][name]
        else:
            if typ3 == "proxy":
                self.lock.release()
                return None
            elif typ3 == "normal" and len(self.active["proxy"]) > 0:
                name = self.active["proxy"].pop(0)
                self.lock.release()
                return self.pool["proxy"][name]
            else:
                self.lock.release()
                return None

    def set(self, browser):
        self.lock.acquire()
        self.active[browser.typ3].append(browser.name)
        self.lock.release()

    def reset(self, browser, domain, reason):
        print(f"{browser.name} is dead. Reason: {domain}/{reason}\nResetting...")
        self.lock.acquire()
        self.pool[browser.typ3].pop(browser.name)
        self.lock.release()
        browser.browser.close()
        if hasattr(browser, 'proxy'):
            self.proxy_pool.report(browser.proxy)
        for _domain in ["facebook", "instagram", "tiktok", "youtube"]:
            for credential_type in ["account", "cookie"]:
                try:
                    credential_obj = getattr(browser, credential_type)
                except:
                    continue
                else:
                    credential = credential_obj.get(_domain)
                    if credential:
                        if _domain == domain and credential_type == reason:
                            self.credential_pool.report(indicators=[domain, reason], credential=credential)
                        else:
                            self.credential_pool.set(indicators=["available", _domain, credential_type], credential=credential)
        self.add(typ3=browser.typ3)
        del browser




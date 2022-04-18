from requests import Session
from requests.cookies import create_cookie
from requests.exceptions import Timeout
import random
from threading import Lock
from module import helper
import json
import re


class Api(Session):
    def __init__(self, name, proxy, token):
        super().__init__()
        self.name = name
        self.headers.update({
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "vi-VN, en-US",
            "Cache-Control": "private, no-cache, no-store, must-revalidate",
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36",
            "Connection": "keep alive"
        })
        proxy_string = f"https://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
        self.proxies = dict(http=proxy_string, https=proxy_string)
        if token is not None:
            self.facebook_token = token["facebook"]
            # self.instagram_token = token["instagram"]
            # self.youtube_token = token["youtube"]


class ApiPool:
    def __init__(self, proxy_pool, credential_pool, browser_pool):
        self.proxy_pool = proxy_pool
        self.credential_pool = credential_pool
        self.browser_pool = browser_pool
        self.pool = dict()
        self.active_api = list()
        self.lock = Lock()

    def add_new_api(self):
        proxy, error = self.proxy_pool.new_proxy()
        if error is not None:
            print(f"Cant add new api, no available proxy.\nDetail: {error}")
            return None
        token = dict()
        for typ3 in ["facebook", "instagram"]:
            _token = None
            while _token is None:
                _token, error = self.browser_pool.generate_token(typ3=typ3)
            token[typ3] = _token
            self.credential_pool.set([typ3, "access_token"], _token)
        self.lock.release()
        name = helper.generate_name(prefix=f"api_", exist_name=self.pool.keys())
        api = Api(name=name, proxy=proxy, token=token)
        self.lock.acquire()
        self.pool[name] = api
        self.active_api.append(name)
        self.lock.release()

    def get_active_api(self):
        self.lock.acquire()
        if len(self.active_api) > 0:
            name = self.active_api.pop(0)
            self.lock.release()
            api = self.pool[name]
            return api, None
        else:
            self.lock.release()
            return None, {"message": "No available api", "status_code": 400}

    def set_active_api(self, api):
        self.lock.acquire()
        self.active_api.append(api.name)
        self.lock.release()

    def reset_api(self, api, mode, typ3):
        self.lock.acquire()
        self.pool.pop(api.name)
        self.lock.release()
        if mode == 'proxy':
            proxies = api.proxies["http"]
            self.proxies['active'].pop(proxies)
            self.proxies['dead'][proxies] = True
        elif mode == 'token':
            for _typ3 in self.tokens:
                token = getattr(api, f"{_typ3}_token")
                if _typ3 == typ3:
                    self.tokens[_typ3]['active'].pop(token)
                    self.tokens[_typ3]['dead'][token] = True
                else:
                    self.tokens[_typ3]["available"][token] = True
                    self.tokens[_typ3]["active"].pop(token)

        api.close()
        self.add_new_api()

    def request(self, url, token, **kwargs):
        api, error = self.get_active_api()
        if error is not None:
            return None, error
        method = kwargs.pop("method")
        typ3 = kwargs.pop("type")
        if token:
            if typ3 == "facebook":
                if "access_token" not in url:
                    kwargs["access_token"] = api.facebook_token
            elif typ3 == "instagram":
                kwargs["access_token"] = api.instagram_token
        if method == "GET":
            params = dict()
            for key, value in kwargs.items():
                if type(value) == list:
                    params[key] = ','.join(value)
                elif type(value) == dict:
                    params[key] = ','.join(list(map(lambda k: f"{k}={value[k]}", value)))
                else:
                    params[key] = value
            kwargs = {"params": params}
        elif method == "POST":
            kwargs = {"data": kwargs}
        print(url)
        print(kwargs)
        try:
            response = api.request(method=method, url=url, **kwargs)
        except Exception as e:
            self.reset_api(api=api, mode="proxy", typ3=None)
            return None, {"message": f"Request error: {str(e)}", "status_code": 400}
        else:
            if "json" in response.headers["Content-Type"]:
                try:
                    data = response.json()
                except Exception as e:
                    return None, {"message": f"Cant {method} {url}. \nDetail: {str(e)}"}
                if data.get("error"):
                    self.reset_api(api=api, mode="token", typ3=typ3)
                    return data, {"message": data["error"], "status_code": 400}
                self.set_active_api(api)
                return data, None

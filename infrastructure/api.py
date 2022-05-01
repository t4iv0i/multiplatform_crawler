from requests import Session


class Api(Session):
    def __init__(self, name=None, typ3=None, proxy=None, token=None, cookie=None):
        super().__init__()
        if name is not None:
            self.name = name
            print(f"Starting {self.name}")
        if typ3 is not None:
            self.typ3 = typ3
        self.headers.update({
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "vi-VN, en-US",
            "Cache-Control": "private, no-cache, no-store",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Connection": "keep alive"
        })
        if proxy is not None:
            self.proxy = proxy
        if token is not None:
            self.token = token
        if cookie is not None:
            self.cookie = cookie

    def set_cookie(self, typ3):
        for cookie_obj in self.cookie[typ3].object:
            self.cookies.set_cookie(cookie_obj)
        print(self.cookies)

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



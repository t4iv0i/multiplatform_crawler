from infrastructure.api import Api
from constant import constant
from requests.cookies import create_cookie
from bs4 import BeautifulSoup
from importlib import import_module


class Credential:
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def to_dict(self):
        return self.__dict__.copy()

    def __repr__(self):
        return str(self.to_dict())


class Account(Credential):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        result = self.to_dict()
        for spare_field in ["typ3"]:
            result.pop(spare_field)
        return str(result)

    def check(self, proxy):
        browser_module = import_module("infrastructure.browser")
        Browser = getattr(browser_module, "Browser")
        browser = Browser(account={self.domain: self})
        cookie, error = browser.generate_cookie(domain=self.domain)
        browser.browser.close()
        if error is not None:
            print(error)
            return False
        else:
            return True


class Token(Credential):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return self.__dict__["token"]

    def check(self, proxy):
        api = Api(proxy=proxy)
        check_url = constant.check_token_url[self.domain]
        try:
            response = api.get(url=check_url, params={"access_token": self.token})
            data = response.json()
        except:
            api.close()
            return None
        else:
            api.close()
            if data.get("error"):
                return False
            else:
                return True


class Cookie(Credential):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = self.get_object()

    def to_dict(self):
        result = self.to_dict()
        result.pop("object")
        return result

    def __repr__(self):
        return str(self.__dict__["cookie"])

    def get_object(self):
        cookie_obj = list()
        for cookie in self.cookie:
            domain, name, value = cookie["domain"], cookie["name"], cookie["value"]
            obj = create_cookie(domain=domain, name=name, value=value)
            cookie_obj.append(obj)
        return cookie_obj

    # def check(self, proxy):
    #     api = Api(proxy=proxy, cookie=self)
    #     check_url, logged_in_selector = constant.check_logged_in_selector[self.domain]
    #     for cookie_obj in self.get_object():
    #         api.cookies.set_cookie(cookie_obj)
    #     try:
    #         response = api.get(url=check_url)
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #     except Exception as e:
    #         print(str(e))
    #         api.close()
    #         return None
    #     else:
    #         api.close()
    #         element = soup.select()
    #         if element is None:
    #             return False
    #         else:
    #             return True

    def check(self, proxy):
        browser_module = import_module("infrastructure.browser")
        Browser = getattr(browser_module, "Browser")
        browser = Browser(proxy=proxy)
        check_url, logged_in_xpath = constant.check_logged_in_xpath[self.domain]
        try:
            browser.browser.get(check_url)
            for cookie in self.cookie:
                browser.browser.add_cookie(cookie)
            element = browser.wait_until_visibility_of_element_located(logged_in_xpath)
        except:
            browser.browser.close()
            return False
        else:
            browser.browser.close()
            return True




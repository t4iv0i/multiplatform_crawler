import re

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from uuid import uuid4
import os
from threading import Lock
from module import helper
from constant import constant


class Browser:
    def __init__(self, name, proxy=None, credential=None):
        self.name = name
        chrome_options = ChromeOptions()
        prefs = dict()
        prefs.update({"profile.managed_default_content_settings.images": 2})
        prefs.update({"profile.default_content_setting_values.notifications": 2})
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        if proxy is not None:
            plugin_path = os.path.join('resources', 'proxy', str(uuid4()) + '.zip')
            plugin_file = helper.create_proxyauth_extension(proxy_host=proxy["hostname"], proxy_username=proxy["username"],
                                                            proxy_password=proxy["password"], proxy_port=proxy["port"],
                                                            plugin_path=plugin_path)
            chrome_options.add_extension(plugin_file)
            self.proxy = proxy
        self.browser = Chrome(executable_path="./chromedriver", options=chrome_options)
        self.browser.maximize_window()
        self.waiter = WebDriverWait(driver=self.browser, timeout=3)
        if credential is not None:
            self.type = "proxy"
            self.credential = credential
        else:
            self.type = "normal"

    def find_element_by_xpath(self, xpath, element=None):
        try:
            if element is None:
                result = self.browser.find_element(By.XPATH, xpath)
            else:
                result = element.find_element(By.XPATH, xpath)
        except Exception as e:
            return None, {"message": f"Can't find element by xpath.\nDetail: {str(e)}", "status_code": 400}
        else:
            return result

    def find_elements_by_xpath(self, xpath, element=None):
        try:
            if element is None:
                result = self.browser.find_elements(By.XPATH, xpath)
            else:
                result = element.find_elements(By.XPATH, xpath)
        except Exception as e:
            return None, {"message": f"Can't find element by xpath.\nDetail: {str(e)}", "status_code": 400}
        else:
            return result

    def wait_until_url_contains(self, url):
        self.waiter.until(EC.url_contains(url))
        return True

    def wait_until_visibility_of_element_located(self, xpath):
        element = self.waiter.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return element
    
    def wait_until_presence_of_element_located(self, xpath):
        element = self.waiter.until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element

    def wait_until_text_to_be_present_in_element(self, xpath, text):
        element = self.waiter.until(EC.text_to_be_present_in_element((By.XPATH, xpath), text))
        return element

    def wait_until_visibility_of(self, element):
        self.waiter.until(EC.visibility_of(element))
        return True

    def wait_until_element_selection_state_to_be(self, element):
        self.waiter.until(EC.element_selection_state_to_be(element, False))
        return True

    def wait_until_staleness_of(self, element):
        self.waiter.until(EC.staleness_of(element))
        return True

    def wait_until_element_located_to_be_selected(self, xpath):
        element = self.waiter.until(EC.element_located_to_be_selected((By.XPATH, xpath)))
        return element

    def wait_until_element_to_be_clickable(self, xpath):
        element = self.waiter.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        return element

    def wait_until_frame_to_be_available_and_switch_to_it(self, xpath):
        element = self.waiter.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))
        return element

    def wait_until_element_attribute_to_include(self, xpath, attribute):
        element = self.waiter.until(EC.element_attribute_to_include((By.XPATH, xpath), attribute))
        return element

    def login_to_facebook(self):
        username, password = self.credential["username"], self.credential["password"]

        cookie = ""
        return cookie

    def login_to_instagram(self):
        username, password = self.credential["username"], self.credential["password"]

        cookie = ""
        return cookie


class BrowserPool:
    def __init__(self, proxy_pool, credential_pool):
        self.proxy_pool = proxy_pool
        self.credential_pool = credential_pool
        self.pool = {"proxy": {}, "normal": {}}
        self.active_browser = {"proxy": [], "normal": []}
        self.lock = Lock()

    def add_new_browser(self, typ3):
        name = helper.generate_name(prefix=f"browser", exist_name=self.pool.keys())
        if typ3 == "proxy":
            proxy = self.proxy_pool.get()
            if proxy is None:
                print("Can't create new browser. No available proxy")
                return None
            facebook_account = self.credential_pool.get(indicators=["facebook", "account"])
            instagram_account = self.credential_pool.get(indicators=["instagram", "account"])
            credential = {"facebook": facebook_account, "instagram": instagram_account}
            browser = Browser(name=name, proxy=proxy, credential=credential)
            facebook_cookie = browser.login_to_facebook()
            if facebook_cookie is not None:
                self.credential_pool.set(indicators=["facebook", "cookie"], credential=facebook_cookie)
            instagram_cookie = browser.login_to_instagram()
            if instagram_cookie is not None:
                self.credential_pool.set(indicators=["instagram", "cookie"], credential=instagram_cookie)
        else:
            browser = Browser(name=name)
        self.lock.acquire()
        self.pool[typ3][name] = browser
        self.active_browser[typ3].append(name)
        self.lock.release()

    def get_inactive_browser(self, typ3):
        self.lock.acquire()
        if len(self.active_browser[typ3]) > 0:
            name = self.active_browser[typ3].pop(0)
            self.lock.release()
            return self.pool[typ3][name]
        else:
            self.lock.release()
            return None

    def set_active_browser(self, browser):
        self.lock.acquire()
        self.active_browser[browser.type].append(browser.name)
        self.lock.release()

    def reset_browser(self, browser, reason):
        self.lock.acquire()
        self.pool.pop(browser.name)
        self.lock.release()
        browser.browser.close()
        if reason == "proxy":
            proxy = browser.proxy
            self.proxy_pool.report(proxy)
            self.add_new_browser(typ3="proxy")
        elif reason == "facebook":
            credential = browser.credential
            self.credential_pool.report(credential["facebook"])
            self.add_new_browser(typ3="proxy")
        elif reason == "instagram":
            credential = browser.credential
            self.credential_pool.report(credential["instagram"])
            self.add_new_browser(typ3="proxy")
        else:
            self.add_new_browser(typ3="normal")
        del browser

    def generate_token(self, typ3):
        browser = self.get_inactive_browser(typ3="proxy")
        if typ3 == "facebook":
            try:
                browser.browser.get(constant.facebook_get_access_token_url)
                browser.wait_until_url_contains("access_token")
            except Exception as e:
                message = f"Can't get {type} token.\nDetail: {str(e)}"
                print(message)
                return None, {"message": message, "status_code": 400}
            else:
                access_token = re.findall("access_token=([^\&]+)\&", browser.browser.current_url)[0]
                return access_token, None
        elif typ3 == "instagram":
            try:
                browser.browser.get(constant.facebook_get_access_token_url)
                browser.wait_until_url_contains("access_token")
            except Exception as e:
                message = f"Can't get {type} token.\nDetail: {str(e)}"
                print(message)
                return None, {"message": message, "status_code": 400}
            else:
                access_token = re.findall("access_token=([^\&]+)\&", browser.browser.current_url)[0]
                return access_token, None



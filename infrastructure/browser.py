import os
import re
from threading import Lock
from uuid import uuid4
from pyotp import TOTP
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from constant import constant
from module import helper
from time import sleep


class Browser:
    def __init__(self, name, proxy=None, account=None):
        self.name = name
        chrome_options = ChromeOptions()
        prefs = dict()
        prefs.update({"profile.managed_default_content_settings.images": 2})
        prefs.update({"profile.default_content_setting_values.notifications": 2})
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        if proxy is not None:
            self.proxy = proxy
            plugin_path = os.path.join('resources', 'proxy', str(uuid4()) + '.zip')
            plugin_file = helper.create_proxyauth_extension(proxy_host=proxy["hostname"], proxy_username=proxy["username"],
                                                            proxy_password=proxy["password"], proxy_port=proxy["port"],
                                                            plugin_path=plugin_path)
            chrome_options.add_extension(plugin_file)
            self.browser = Chrome(executable_path="./chromedriver", options=chrome_options)
            os.remove(plugin_file)
        else:
            self.browser = Chrome(executable_path="./chromedriver", options=chrome_options)
        self.browser.maximize_window()
        self.explicit_wait = WebDriverWait(driver=self.browser, timeout=30)
        self.implicit_wait = self.browser.implicitly_wait
        if account is not None:
            self.typ3 = "proxy"
            self.account = account
            self.cookie = dict()
        else:
            self.typ3 = "normal"

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
        self.explicit_wait.until(EC.url_contains(url))
        return True

    def wait_until_visibility_of_element_located(self, xpath):
        element = self.explicit_wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return element

    def wait_until_presence_of_element_located(self, xpath):
        element = self.explicit_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element

    def wait_until_text_to_be_present_in_element(self, xpath, text):
        element = self.explicit_wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath), text))
        return element

    def wait_until_visibility_of(self, element):
        self.explicit_wait.until(EC.visibility_of(element))
        return True

    def wait_until_element_selection_state_to_be(self, element):
        self.explicit_wait.until(EC.element_selection_state_to_be(element, False))
        return True

    def wait_until_staleness_of(self, element):
        self.explicit_wait.until(EC.staleness_of(element))
        return True

    def wait_until_element_located_to_be_selected(self, xpath):
        element = self.explicit_wait.until(EC.element_located_to_be_selected((By.XPATH, xpath)))
        return element

    def wait_until_element_to_be_clickable(self, xpath):
        element = self.explicit_wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        return element

    def wait_until_frame_to_be_available_and_switch_to_it(self, xpath):
        element = self.explicit_wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))
        return element

    def wait_until_element_attribute_to_include(self, xpath, attribute):
        element = self.explicit_wait.until(EC.element_attribute_to_include((By.XPATH, xpath), attribute))
        return element

    def login_to_facebook(self):
        account = self.account["facebook"]
        self.browser.get("https://mbasic.facebook.com")
        try:
            self.explicit_wait.until(EC.presence_of_element_located((By.XPATH, constant.mbasic_facebook_email_xpath)))
            username_element = self.browser.find_element(By.XPATH, constant.mbasic_facebook_email_xpath)
            self.explicit_wait.until(EC.visibility_of(username_element))
        except:
            self.browser.close()
            return None
        username_element.send_keys(account["username"])
        try:
            self.explicit_wait.until(EC.presence_of_element_located((By.XPATH, constant.mbasic_facebook_password_xpath)))
            password_element = self.browser.find_element(By.XPATH, constant.mbasic_facebook_password_xpath)
            self.explicit_wait.until(EC.visibility_of(password_element))
        except:
            self.browser.close()
            return None
        password_element.send_keys(account["password"])
        try:
            self.explicit_wait.until(EC.presence_of_element_located((By.XPATH, constant.mbasic_facebook_login_button_xpath)))
            login_button = self.browser.find_element(By.XPATH, constant.mbasic_facebook_login_button_xpath)
            self.explicit_wait.until(EC.visibility_of(login_button))
        except:
            self.browser.close()
            return None
        login_button.click()
        token = account.get("token")
        if token:
            sleep(30)
            two_factor = TOTP(token).now()
            step_two = self.browser.find_element(By.XPATH, constant.mbasic_facebook_2fa_input_xpath)
            self.explicit_wait.until(EC.visibility_of(step_two))
            step_two.send_keys(two_factor)
            self.wait_until_element_to_be_clickable(constant.mbasic_facebook_next_button_xpath)
            next_button = self.browser.find_element(By.XPATH, constant.mbasic_facebook_next_button_xpath)
            next_button.click()
            self.wait_until_element_to_be_clickable(constant.mbasic_facebook_2fa_dont_save_xpath)
            do_not_save = self.browser.find_element(By.XPATH, constant.mbasic_facebook_2fa_dont_save_xpath)
            do_not_save.click()
        while True:
            try:
                self.wait_until_element_to_be_clickable(constant.mbasic_facebook_next_button_xpath)
                next_button = self.browser.find_element(By.XPATH, constant. mbasic_facebook_next_button_xpath)
                next_button.click()
            except:
                break
        print("Started Chrome")
        cookie = self.browser.get_cookies()
        self.cookie["facebook"] = cookie
        return cookie

    def login_to_instagram(self):
        username, password = self.account["username"], self.account["password"]

        cookie = []
        self.cookie["instagram"] = cookie
        return cookie

    def login_to_youtube(self):
        email, password = self.account["email"], self.account["password"]

        cookie = []
        self.cookie["tiktok"] = cookie
        return cookie

    def login_to_tiktok(self):
        email, password = self.account["email"], self.account["password"]

        cookie = []
        self.cookie["titok"] = cookie
        return cookie


class BrowserPool:
    def __init__(self, proxy_pool, credential_pool):
        self.proxy_pool = proxy_pool
        self.credential_pool = credential_pool
        self.pool = {"proxy": {}, "normal": {}}
        self.active = {"proxy": [], "normal": []}
        self.lock = Lock()

    def add(self, typ3):
        name = helper.generate_name(prefix=f"browser", exist_name=self.pool.keys())
        if typ3 == "proxy":
            # proxy = self.proxy_pool.get()
            # if proxy is None:
            #     print("Can't create new browser. No available proxy")
            #     return None
            account = dict()
            for domain in ["facebook"]:
                _account = self.credential_pool.get(indicators=[domain, "account"])
                if _account is None:
                    print(f"No {domain} account available")
                    return None
                account[domain] = _account
            browser = Browser(name=name, proxy=None, account=account)
            facebook_cookie = browser.login_to_facebook()
            if facebook_cookie is not None:
                self.credential_pool.set(indicators=["facebook", "cookie"], credential=facebook_cookie)
            # instagram_cookie = browser.login_to_instagram()
            # if instagram_cookie is not None:
            #     self.credential_pool.set(indicators=["instagram", "cookie"], credential=instagram_cookie)
        else:
            browser = Browser(name=name)
            # youtube_cookie = browser.login_to_youtube()
            # if youtube_cookie is not None:
            #     self.credential_pool.set(indicators=["youtube", "cookie"], credential=youtube_cookie)
            # youtube_cookie = browser.login_to_tiktok()
            # if tiktok_cookie is not None:
            #     self.credential_pool.set(indicators=["tiktok", "cookie"], credential=tiktok_cookie)
        self.lock.acquire()
        self.pool[typ3][name] = browser
        self.active[typ3].append(name)
        self.lock.release()

    def get_active(self, typ3):
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

    def set_active(self, browser):
        self.lock.acquire()
        self.active[browser.type].append(browser.name)
        self.lock.release()

    def reset(self, browser, typ3, reason):
        print(f"{browser.name} is dead. Reason: {typ3}/{reason}\nResetting...")
        self.lock.acquire()
        self.pool[browser.typ3].pop(browser.name)
        self.lock.release()
        proxy = browser.proxy
        self.proxy_pool.report(proxy)
        for domain in ["facebook", "instagram", "tiktok", "youtube"]:
            for credential_type in ["account", "cookie"]:
                try:
                    credential_obj = getattr(browser, credential_type)
                except:
                    continue
                else:
                    credential = credential_obj.get(domain)
                    if credential:
                        if domain == typ3 and credential_type == reason:
                            self.credential_pool.report(indicators=[typ3, reason], credential=credential)
                        else:
                            self.credential_pool.set(indicators=[domain, credential_type], credential=credential)
        browser.browser.close()
        self.add(typ3=browser.typ3)
        del browser

    def generate_token(self, typ3):
        if typ3 == "facebook":
            browser = self.get_active(typ3="proxy")
            try:
                browser.browser.get(constant.facebook_get_access_token_url)
                browser.wait_until_url_contains("access_token")
            except Exception as e:
                self.set_active(browser)
                return None, {"message": f"Can't get {type} token.\nDetail: {str(e)}", "status_code": 400}
            else:
                access_token = re.findall("access_token=([^\&]+)\&", browser.browser.current_url)[0]
                self.set_active(browser)
                return access_token, None
        elif typ3 == "instagram":
            browser = self.get_active(typ3="proxy")
            access_token = ""
            self.set_active(browser)
            return access_token, None
        elif typ3 == "youtube":
            browser = self.get_active(typ3="normal")
            access_token = ""
            self.set_active(browser)
            return access_token, None
        elif typ3 == "tiktok":
            browser = self.get_active(typ3="normal")
            access_token = ""
            self.set_active(browser)
            return access_token, None


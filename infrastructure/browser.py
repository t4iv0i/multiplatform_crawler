from infrastructure.credential import Token, Cookie
from constant import constant
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pyotp import TOTP
import os, re


class Browser:
    def __init__(self, name=None, proxy=None, account=None):
        if name is not None:
            self.name = name
            print(f"Starting {self.name}")
        chrome_options = ChromeOptions()
        prefs = dict()
        prefs.update({"profile.managed_default_content_settings.images": 2})
        prefs.update({"profile.default_content_setting_values.notifications": 2})
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        if proxy is not None:
            self.proxy = proxy
            chrome_options.add_argument(f"--proxy-server={proxy.server()}")
            if hasattr(proxy, "username"):
                plugin_file = proxy.plugin_file()
                chrome_options.add_extension(plugin_file)
                # os.remove(plugin_file)
        self.browser = Chrome(executable_path="/home/t4iv0i/PycharmProjects/multiplatform_crawler/resources/environment/chromedriver", options=chrome_options)
        self.browser.maximize_window()
        self.explicit_wait = WebDriverWait(driver=self.browser, timeout=constant.BROWSER_TIMEOUT)
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

    def generate_cookie(self, domain):
        login_url, check_logged_in_xpath = constant.check_logged_in_xpath[domain]
        if domain == "facebook":
            account = self.account["facebook"]
            try:
                self.browser.get(login_url)
                self.wait_until_visibility_of_element_located(check_logged_in_xpath)
            except:
                try:
                    username = self.wait_until_visibility_of_element_located(constant.mbasic_facebook_email_xpath)
                    self.wait_until_visibility_of(username)
                    username.send_keys(account.username)
                    password = self.wait_until_visibility_of_element_located(constant.mbasic_facebook_password_xpath)
                    self.wait_until_visibility_of(password)
                    password.send_keys(account.password)
                    login_button = self.wait_until_element_to_be_clickable(constant.mbasic_facebook_login_button_xpath)
                    login_button.click()
                    if hasattr(account, "secret_2fa"):
                        two_factor = TOTP(account.secret_2fa).now()
                        step_two = self.wait_until_visibility_of_element_located(constant.mbasic_facebook_2fa_input_xpath)
                        self.wait_until_visibility_of(step_two)
                        step_two.send_keys(two_factor)
                        next_button = self.wait_until_element_to_be_clickable(constant.mbasic_facebook_next_button_xpath)
                        next_button.click()
                        do_not_save = self.wait_until_element_to_be_clickable(constant.mbasic_facebook_2fa_dont_save_xpath)
                        do_not_save.click()
                except:
                    pass
                else:
                    for tries in range(5):
                        try:
                            next_button = self.wait_until_element_to_be_clickable(constant.mbasic_facebook_next_button_xpath)
                            next_button.click()
                        except:
                            break
                try:
                    self.wait_until_visibility_of_element_located(check_logged_in_xpath)
                except:
                    return None, f"Can't generate {domain} cookie from {account}"
            cookie = Cookie(typ3="cookie", domain=domain, cookie=self.browser.get_cookies())
            self.cookie[domain] = cookie
            return cookie, None
        elif domain == "instagram":
            account = self.account["instagram"]
            try:
                self.browser.get(login_url)
                self.wait_until_visibility_of_element_located(check_logged_in_xpath)
            except:
                try:
                    instagram_continue_button = self.wait_until_element_to_be_clickable(constant.instagram_continue_button_xpath)
                    instagram_continue_button.click()
                except:
                    try:
                        username = self.wait_until_visibility_of_element_located(constant.instagram_username_xpath)
                        self.wait_until_visibility_of(username)
                        username.send_keys(account.username)
                        password = self.wait_until_visibility_of_element_located(constant.instagram_password_xpath)
                        self.wait_until_visibility_of(password)
                        password.send_keys(account.password)
                        login_button = self.wait_until_element_to_be_clickable(constant.instagram_login_button_xpath)
                        login_button.click()
                        not_save_button = self.wait_until_element_to_be_clickable(constant.instagram_not_save_button_xpath)
                        not_save_button.click()
                        self.wait_until_visibility_of_element_located(check_logged_in_xpath)
                    except:
                        return None, f"Can't generate {domain} cookie"
            cookie = Cookie(typ3="cookie", domain=domain, cookie=self.browser.get_cookies())
            self.cookie[domain] = cookie
            return cookie, None

    def generate_token(self, typ3):
        if typ3 == "facebook":
            try:
                self.browser.get(constant.facebook_get_access_token_url)
                self.wait_until_url_contains("access_token")
            except Exception as e:
                return None, f"Can't get {typ3} token.\nDetail: {str(e)}"
            access_token = re.findall("access_token=([^\&]+)\&", self.browser.current_url)[0]
            token = Token(typ3="token", domain="facebook", token=access_token)
            return token, None


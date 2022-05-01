import string, zipfile
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
import os
from uuid import uuid4
import json


def create_proxyauth_extension(proxy_host, proxy_port,
                               proxy_username, proxy_password,
                               scheme, plugin_path=None):
    if plugin_path is None:
        plugin_path = 'resources/proxy/extensions/proxy_auth_plugin.zip'
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = string.Template(
    """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "${scheme}",
                host: "${host}",
                port: parseInt(${port})
              },
              bypassList: ["foobar.com"]
            }
          };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "${username}",
                password: "${password}"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path


def init_browser(proxy=None):
    chrome_options = ChromeOptions()
    prefs = dict()
    prefs.update({"profile.managed_default_content_settings.images": 2})
    prefs.update({"profile.default_content_setting_values.notifications": 2})
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    if proxy is not None:
        plugin_path = os.path.join('resources', 'proxy', 'extensions', str(uuid4()) + '.zip')
        # plugin_file = create_proxyauth_extension(scheme=proxy["scheme"], proxy_host=proxy["hostname"], proxy_username=proxy["username"],
        #                                          proxy_password=proxy["password"], proxy_port=proxy["port"],
        #                                          plugin_path=plugin_path)
        # chrome_options.add_extension(plugin_file)
        proxy_string = f'{proxy["scheme"]}://{proxy["hostname"]}:{proxy["port"]}'
        chrome_options.add_argument(f"--proxy-server={proxy_string}")
    browser = Chrome(executable_path="./resources/environment/chromedriver", options=chrome_options)
    return browser


with open("resources/proxy/fast/vietproxy_http.json", "rt") as fp:
    proxies = json.load(fp)

for proxy in proxies:
    print(proxy)
    browser = init_browser(proxy)
    for site in [
                 # "https://api.ipify.org",
                 "https://api6.ipify.org",
                 "https://mbasic.facebook.com",
                 "https://www.facebook.com",
                 "https://www.instagram.com"]:
        try:
            browser.get(site)
        except Exception as e:
            print(f"Error")
        else:
            text = browser.find_element(By.XPATH, "/html/body").text
            if "This site can’t be reached" in text or "Your connection was interrupted" in text:
                print(f"{site}: Error")
            else:
                print(f"{site}: Ok")
    browser.close()

# proxy = {"scheme": "http", "username": "VNS65371", "password": "dzgfhhfh", "hostname": "14.225.50.163", "port": 56789}
# browser = init_browser(proxy)
# _ = input()

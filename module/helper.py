from selenium.webdriver.common.by import By
import re, string, zipfile, json
from constant import constant
from datetime import datetime, timedelta, timezone
from os import path, listdir
from os import remove


def normalize_link(url):
    for typ3 in constant.url_patterns:
        for pattern in constant.url_patterns[typ3]:
            normalized_url = re.findall(pattern, url)
            if normalized_url:
                return typ3, "https://" + normalized_url[0]
    return None, None


def instagram_get_username_from_url(url):
    username = re.findall(r'instagram\.com/([^/\?]+)', url)
    if len(username):
        return username[0]
    else:
        return None


def generate_name(prefix, exist_name):
    index = len(exist_name)
    list_browser_name = [f"{prefix}_{i}" for i in range(1, index + 2)]
    return (set(list_browser_name) - set(exist_name)).pop()


def normalize_hashtag(hashtag):
    if hashtag.startswith('#'):
        return hashtag[1:].upper()
    else:
        return hashtag.upper()


def parse_time_delta(duration):
    for timestamp in ["minutes", "hours", "days", "weeks"]:
        if timestamp in duration:
            try:
                period = int(duration.replace(timestamp, ''))
            except:
                return None, {"message": "Period must be int"}
            params = {timestamp: period}
            return timedelta(**params)
    else:
        return None


def remove_id(record):
    if type(record) in [str, int, bool]:
        return record
    elif type(record) == dict:
        if len(list(record.keys())) > 1:
            _ = record.pop("id", None)
            for field in record:
                record[field] = remove_id(record[field])
    elif hasattr(record, '__iter__'):
        record = list(record)
        for index in range(len(record)):
            record[index] = remove_id(record[index])
    return record


def recursive_insert(origin, data, path):
    if path == '':
        if type(origin) == dict:
            origin.update(data)
        elif type(origin) == list:
            origin += data
        return origin
    elif path == '[]':
        return [data]
    pointer, new_path = None, ''
    if path.startswith('{'):
        pointer = re.findall(r'^\{(\w+)\}', path)[0]
        new_path = path[len(pointer) + 2:]
    elif path.startswith('['):
        pointer = re.findall(r'^\[(\d*)\]', path)[0]
        new_path = path[len(pointer) + 2:]
        pointer = int(pointer)
    if pointer:
        origin[pointer] = recursive_insert(origin=origin[pointer], data=data, path=new_path)
    return origin


def recursive_update(source, dest):
    if dest is None:
        return source
    elif type(source) == list and type(dest) == list:
        dest += source
    elif type(source) == dict and type(dest) == dict:
        for key in source:
            dest[key] = recursive_update(source[key], dest.get(key))
    return dest


def create_proxyauth_extension(proxy_host, proxy_port,
                               proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
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


def scan(root_dir, pattern=None, json_type=False):
    names, result = listdir(root_dir), list()
    for name in names:
        file_path = path.join(root_dir, name)
        if not path.isdir(file_path):
            with open(file_path, 'rt') as fp:
                if pattern:
                    for line in fp:
                        result += re.findall(pattern, line.strip())
                elif json_type:
                    try:
                        data = json.load(fp)
                    except:
                        continue
                    if type(data) == list:
                        for record in data:
                            if record not in result:
                                result.append(record)
                    elif type(data) == dict:
                        result.append(data)
            # remove(file_path)
    return result

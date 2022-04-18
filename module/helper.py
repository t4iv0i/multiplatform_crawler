from selenium.webdriver.common.by import By
import re, string, zipfile, json
from constant import constant
from datetime import datetime, timedelta, timezone
from os import path, listdir


def normalize_link(url):
    for typ3 in constant.url_patterns:
        for pattern in constant.url_patterns[typ3]:
            normalized_url = re.findall(pattern, url)
            if normalized_url:
                return typ3, "https://" + normalized_url[0]
    return None, None


def url_join_facebook_personal_page(url, sub):
    link = url
    if "?id=" in url:
        link += f"&sk={sub}"
    else:
        link += f"/{sub}"
    return link


def url_join(url, sub):
    return f"{url}/{sub}"


def url_join_facebook_about(url):
    if re.match(r'.*facebook\.com/profile\.php\?id=', url):
        return url + '&sk=about'
    else:
        return url + '/about'


def read_file(file_name):
    text = ""
    with open(file_name, 'rt') as fp:
        for line in fp:
            text += line
    return text


def number_extractor(text):
    try:
        number_text, unit_text = re.findall(r'(\d+[\.\,]*\d*[\.\,]*\d*[\.\,]*\d*[\.\,]*\d*)\s*(\w*)', text)[0]
    except:
        return None
    number, unit = number_text.replace(',', '.'), unit_text.upper()
    if constant.teen_code.get(unit):
        return int(float(number) * constant.teen_code[unit])
    else:
        return int(number.replace('.', ''))


def normalize_info(info, typ3):
    result = dict()
    follower = 0
    for field in info:
        if field in constant.number_fields[typ3] and type(info[field]) == str:
            num_field = number_extractor(info[field])
            if num_field is not None:
                result[field] = num_field
                if field in ["follower", "friend", "member"]:
                    follower += num_field
            else:
                result[field] = info[field]
        elif field == "hashtag" and type(info[field]) == str:
            result["hashtag"] = True
        else:
            result[field] = info[field]
    if follower > 0:
        result["follower"] = follower
    return result


def normalize_info_old(info):
    result = dict()
    for field, value in info.items():
        if type(value) == list:
            spare = list()
            for item in value:
                if type(item) == dict:
                    new_item = normalize_info(item)
                    result = update_info(result, new_item)
                else:
                    spare.append(item)
            if spare:
                result[field] = spare
        elif type(value) == dict:
            new_value = normalize_info(info[field])
            result = update_info(result, new_value)
        elif type(value) == str:
            if value in constant.personal_fields or re.match(r'^\d{4}\s+-', value):
                result[value] = field
            elif "KhÃ´ng cÃ³" in value:
                result[field] = ""
            else:
                if result.get(field):
                    if type(result[field]) == list:
                        result[field].append(value)
                    else:
                        result[field] = [result[field], value]
                else:
                    result[field] = value
        else:
            result[field] = value
    return result


def find_multiple_content(elements):
    num_content, content_elements = 0, []
    for element in elements:
        if element.text != "":
            num_content += 1
            content_elements.append(element)
    if num_content == 0 or num_content >= 2:
        return content_elements
    else:
        has_content = find_multiple_content(content_elements[0].find_elements(By.XPATH, "./*"))
        if has_content:
            return has_content
        else:
            return content_elements


def parse_html_to_dict(element):
    if element.tag_name == 'span':
        return element.text
    sub_elements = element.find_elements(By.XPATH, "./*")
    if len(sub_elements) == 0:
        return element.text
    content_elements = []
    for sub_element in sub_elements:
        if sub_element.text != "":
            content_elements.append(sub_element)
    if len(content_elements) == 1:
        return parse_html_to_dict(content_elements[0])
    elif len(content_elements) > 1:
        data = list()
        for content_element in content_elements:
            sub_content = parse_html_to_dict(content_element)
            if sub_content:
                if type(sub_content) == list and len(sub_content) == 1:
                    sub_content = sub_content[0]
                data.append(sub_content)
        if type(data[0]) == str and len(data) > 0:
            result = dict()
            result[data[0]] = data[1] if len(data) == 2 else data[1:]
            return result
        elif all([type(item) == dict for item in data]):
            result = dict()
            for item in data:
                for field in item:
                    result[field] = item[field]
            return result
        else:
            return data
    return None


def parse_duration(duration):
    num, unit = re.findall(r'(\d+\.*\d*)\s*(\w+)', duration)[0]
    params = dict()
    params[unit] = float(num)
    to_datetime = datetime.now(timezone.utc)
    from_datetime = to_datetime - timedelta(**params)
    return from_datetime


def update_info(dest, source):
    result = dest.copy()
    for field in source:
        if result.get(field):
            if type(result[field]) == list:
                result[field].append(source[field])
            else:
                result[field] = [result[field], source[field]]
        else:
            result[field] = source[field]
    return result


def convert_facebook_web_to_mobile(url):
    return url.replace("www", "m")


def parse_article(article, datetime_xpath, content_xpath):
    result = dict()
    try:
        _datetime = article.find_element(By.XPATH, datetime_xpath)
    except Exception as e:
        print(e)
        return result
    _datetime = _datetime.text
    if "Vá»«a xong" in _datetime:
        dt = datetime.now() - timedelta(hours=1)
    elif "HÃ´m qua" in _datetime:
        _datetime = re.findall(r'^(.+:\d{2})', _datetime)[0]
        hour, minute = re.findall(r'(\d+):(\d+)', _datetime)[0]
        dt = datetime.now() - timedelta(days=1)
        minute, hour, day, month, year = int(minute), int(hour), int(dt.strftime("%d")), int(dt.strftime("%m")), int(dt.strftime("%Y"))
        dt = datetime.strptime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
    elif "phÃºt" in _datetime:
        minutes = re.findall(r'^(\d+)\s+', _datetime)[0]
        dt = datetime.now() - timedelta(minutes=int(minutes))
    elif "giá»" in _datetime:
        hour = re.findall(r'^(\d+)\s+', _datetime)[0]
        dt = datetime.now() - timedelta(hours=int(hour))
    elif "lÃºc" in _datetime:
        _datetime = re.findall(r'^(.+:\d{2})', _datetime)[0]
        if ',' in _datetime:
            day, month, year, hour, minute = re.findall(r'^(\d+)\s+.+\s+(\d+),\s+(\d+)\s+.+\s+(\d+):(\d+)', _datetime)[0]
        else:
            day, month, hour, minute = re.findall(r'^(\d+)\s+.+\s+(\d+)\s+.+\s+(\d+):(\d+)', _datetime)[0]
            year = datetime.now().strftime('%Y')
        day, month, year, hour, minute = int(day), int(month), int(year), int(hour), int(minute)
        dt = datetime.strptime(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
    else:
        return result
    result['datetime'] = dt
    try:
        content_elements = article.find_elements(By.XPATH, content_xpath)
    except:
        return result
    content = list()
    for element in content_elements:
        text = element.text
        if text:
            content.append(text)
    result["content"] = content
    return result


def view_page_source(url):
    return f"view-source:{url}"


def instagram_get_username_from_url(url):
    username = re.findall(r'instagram\.com/([^/\?]+)', url)
    if len(username):
        return username[0]
    else:
        return None


def youtube_get_id_from_url(url):
    identity = re.findall(r'youtube\.com/[Cchanel]+/([^/\?]+)', url)
    if len(identity):
        return identity[0]
    return None


def tiktok_get_username_from_url(url):
    identity = re.findall(r'tiktok\.com/@([^/\?]+)', url)
    if len(identity):
        return identity[0]
    return None


def generate_facebook_url(url):
    profile_id = re.findall(r'facebook\.com/profile\.php\?id=([^/]+)', url)
    if len(profile_id):
        mobile_url = f"https://m.facebook.com/profile.php?id={profile_id[0]}"
        web_url = f"https://www.facebook.com/profile.php?id={profile_id[0]}"
        return mobile_url, web_url
    group_id = re.findall(r'[^/]*facebook\.com/groups/([^/\?]+)', url)
    if len(group_id):
        mobile_url = f"https://m.facebook.com/groups/{group_id[0]}"
        web_url = f"https://www.facebook.com/groups/{group_id[0]}"
        return mobile_url, web_url
    username = re.findall(r'facebook\.com/([^/\?]+)', url)
    if len(username):
        mobile_url = f"https://m.facebook.com/{username[0]}"
        web_url = f"https://www.facebook.com/{username[0]}"
        return mobile_url, web_url
    else:
        return None, None


def query_string_json(text, indicators, pattern):
    if len(indicators) > 1:
        try:
            indicator = indicators[0]
            start = text.index(indicator) + len(indicator) + 1
        except:
            return None
        else:
            idx, bracket = start + 1, 1
            while bracket > 0 and idx < len(text):
                if text[idx] == '{':
                    bracket += 1
                elif text[idx] == '}':
                    bracket -= 1
                idx += 1
            end = idx + 1
            return query_string_json(text[start: end], indicators[1:], pattern)
    elif len(indicators) == 1:
        try:
            indicator = indicators[0]
            start = text.index(indicator) + len(indicator) + 1
        except:
            return None
        else:
            extractor = re.findall(pattern, text[start:-1])
            if extractor:
                return extractor[0]
            else:
                return None


def facebook_get_fanpage_id(url):
    identity = re.findall(r'facebook\.com/([^/]+)', url)
    if identity:
        return identity[0]
    else:
        return None


def facebook_get_group_id(url):
    group_id = re.findall(r'facebook\.com/groups/([^/]+)', url)
    if group_id:
        return group_id[0]
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


def filter_fields(fields, exclude):
    return list(filter(lambda x: not x.startswith('_') and x not in exclude, fields))


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
        file_path = path.join("resources/proxy", name)
        if not path.isdir(file_path):
            with open(file_path, 'rt') as fp:
                if pattern:
                    for line in fp:
                        result += re.findall(pattern, line.strip())
                elif json_type:
                    result += json.load(fp)
    return result
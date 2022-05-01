from app import api_pool, browser_pool
from module import helper
from bs4 import BeautifulSoup
import re


def get_user_id(url):
    html, error = api_pool.request(url=url, domain="tiktok", method="GET")
    if error is not None:
        return None, error
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.select_one('script[id="sigi-persisted-data"]')
    regex = re.findall(r'\"authorId\":\"(\d+)\"', script.text)
    if regex:
        return regex[0], None
    else:
        return None, {"message": f"Can't get id of {url}", "status_code": 400}


def get_info(url, field_info):
    info = dict()
    crawler = browser_pool.get(typ3="normal")
    try:
        crawler.browser.get(url)
    except Exception as e:
        browser_pool.reset(browser=crawler, domain="tiktok", reason="unknown")
        return None, {"message": f"Can't load page.\nDetail: {str(e)}", "status_code": 400}
    for field in field_info:
        xpath = field_info[field].get("xpath")
        if xpath is None:
            continue
        try:
            crawler.wait_until_presence_of_element_located(xpath)
            element = crawler.browser.find_element_by_xpath(xpath)
            crawler.wait_until_visibility_of(element)
        except Exception as e:
            browser_pool.set(crawler)
            return None, {"message": f"Can't get {field} info.\nDetail: {str(e)}", "status_code": 400}
        else:
            info[field] = element.text
    browser_pool.set(crawler)
    for field in ["follower_count", "following_count", "like_count"]:
        if info.get(field):
            info[field] = helper.number_extractor(info[field])
    return info, None

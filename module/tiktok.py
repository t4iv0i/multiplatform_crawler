from app import browser_pool
from selenium.webdriver.common.by import By
from constant import constant
from module import helper
import re


def get_info(url, hashtag):
    crawler = browser_pool.get_inactive_browser(typ3="tiktok")
    info = dict(url=url)
    try:
        crawler.browser.get(url)
        crawler.wait_presence_of_element_located("/html/body")
        body = crawler.browser.find_element(By.XPATH, "html/body")
        crawler.wait_visibility_of(body)
        text = body.text.lower()
    except:
        return "Cant load page"
    if "Your connection was interrupted" in text or "No internet" in text:
        return "Lost connection"
    for field in constant.tiktok_info_xpath:
        xpath = constant.tiktok_info_xpath[field]
        try:
            crawler.wait_presence_of_element_located(xpath)
            element = crawler.browser.find_element(By.XPATH, constant.tiktok_info_xpath[field])
            crawler.wait_visibility_of(element)
        except:
            pass
        else:
            if field == 'share_link':
                info[field] = element.get_attribute('href')
            else:
                info[field] = element.text
    try:
        username = helper.tiktok_get_username_from_url(crawler.browser.current_url)
        if username:
            info["id"] = username
    except:
        pass
    info["hashtag"] = False
    hashtags = re.findall(r'#(.+)$', hashtag.upper())
    if hashtags:
        hashtag_upper = hashtags[0]
    else:
        hashtag_upper = hashtag.upper()
    if info.get("description"):
        if hashtag_upper in info["description"].upper():
            info["hashtag"] = True
    return info
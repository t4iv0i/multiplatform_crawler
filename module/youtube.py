from app import browser_pool
from selenium.webdriver.common.by import By
from constant import constant
from module import helper
import re


def find_child_have_multiple_content(crawler, elements):
    num_content, content_elements = 0, []
    for element in elements:
        try:
            crawler.wait_visibility_of(element)
            if element.text != "":
                num_content += 1
                content_elements.append(element)
        except:
            pass
    if num_content == 0 or num_content >= 2:
        return content_elements
    else:
        sub_elements = content_elements[0].find_elements(By.XPATH, "./*")
        has_content = find_child_have_multiple_content(crawler, sub_elements)
        if has_content:
            return has_content
        else:
            return content_elements


def get_info(url, hashtag):
    crawler = browser_pool.get_inactive_browser(typ3="youtube")
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
    try:
        crawler.wait_presence_of_element_located("//*[@id='tabsContent']")
        tab_content = crawler.browser.find_element_by_id("tabsContent")
        crawler.wait_visibility_of(tab_content)
    except:
        return info
    for element in find_child_have_multiple_content(crawler, [tab_content]):
        if element.text.lower() == "about":
            element.click()
    for field in constant.youtube_info_xpath:
        xpath = constant.youtube_info_xpath[field]
        try:
            crawler.wait_presence_of_element_located(xpath)
            element = crawler.browser.find_element(By.XPATH, xpath)
            crawler.wait_visibility_of(element)
        except:
            pass
        else:
            info[field] = element.text
    try:
        _id = helper.youtube_get_id_from_url(crawler.browser.current_url)
        if _id:
            info['id'] = _id
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
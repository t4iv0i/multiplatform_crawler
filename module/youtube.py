from app import api_pool, browser_pool
from module import helper
from bs4 import BeautifulSoup


def get_channel_id(url):
    html, error = api_pool.request(url=url, domain="youtube", method="GET")
    if error is not None:
        return None, error
    soup = BeautifulSoup(html, "html.parser")
    try:
        channel_id = soup.select_one('meta[itemprop="channelId"]')['content']
    except Exception as e:
        return None, {"message": f"Can't get channel id.\nDetail: {str(e)}", "status_code": 400}
    else:
        return channel_id, None


def get_fields_info(browser, field_info, fields):
    info = dict()
    for field in fields:
        if field in field_info:
            xpath = field_info[field].get("xpath")
            if xpath is None:
                continue
            try:
                browser.wait_until_presence_of_element_located(xpath)
                element = browser.browser.find_element_by_xpath(xpath)
                browser.wait_until_visibility_of(element)
            except Exception as e:
                return None, {"message": f"Can't get {field} info.\nDetail: {str(e)}", "status_code": 400}
            else:
                info[field] = element.text
    return info, None


def get_info(channel_id, field_info):
    data = {"id": channel_id}
    url = f"https://www.youtube.com/channel/{channel_id}"
    crawler = browser_pool.get(typ3="normal")
    if crawler is None:
        return None, {"message": "Can't get youtube info, no browser available"}
    try:
        crawler.browser.get(url)
    except Exception as e:
        browser_pool.reset(browser=crawler, domain="youtube", reason="unknown")
        return None, {"message": f"Cant load page.\nDetail: {str(e)}", "status_code": 400}
    info, error = get_fields_info(browser=crawler, field_info=field_info, fields=["name", "subscriber_count"])
    if error is not None:
        browser_pool.set(browser=crawler)
        return None, error
    else:
        info.update(info)
    about_url = f"https://www.youtube.com/channel/{channel_id}/about"
    try:
        crawler.browser.get(about_url)
    except Exception as e:
        browser_pool.reset(browser=crawler, domain="youtube", reason="unknown")
        return None, {"message": f"Cant load {about_url} page.\nDetail: {str(e)}", "status_code": 400}
    info, error = get_fields_info(browser=crawler, field_info=field_info, fields=["view_count", "description", "detail", "date_joined"])
    if error is not None:
        browser_pool.set(browser=crawler)
        return None, error
    else:
        info.update(info)
    browser_pool.set(crawler)
    for field in ["subscriber_count", "view_count"]:
        if data.get(field):
            data[field] = helper.number_extractor(data[field])
    browser_pool.set(browser=crawler)
    return info, None

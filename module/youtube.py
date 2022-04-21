from app import api_pool, browser_pool
from bs4 import BeautifulSoup


def get_channel_id(url):
    html, error = api_pool.request(url=url, typ3="youtube", method="GET")
    if error is not None:
        return None, error
    soup = BeautifulSoup(html, "html.parser")
    try:
        channel_id = soup.select_one('meta[itemprop="channelId"]')['content']
    except Exception as e:
        return None, {"message": f"Can't get channel id.\nDetail: {str(e)}", "status_code": 400}
    else:
        return channel_id, None


def get_info(url, field_info):
    info = dict()
    crawler = browser_pool.get_active(typ3="normal")
    try:
        crawler.browser.get(url)
    except Exception as e:
        browser_pool.reset(browser=crawler, reason="youtube")
        return None, {"message": f"Cant load page.\nDetail: {str(e)}", "status_code": 400}
    for field in field_info:
        xpath = field_info[field].get("xpath")
        if xpath is None:
            continue
        try:
            crawler.wait_presence_of_element_located(xpath)
            element = crawler.browser.find_element_by_xpath(xpath)
            crawler.wait_visibility_of(element)
        except Exception as e:
            browser_pool.set_active(crawler)
            return None, {"message": f"Can't get {field} info.\nDetail: {str(e)}", "status_code": 400}
        else:
            info[field] = element.text
    browser_pool.set_active(crawler)
    return info, None

from app import api_pool
from constant import constant
from module import helper


def get_info_api(url):
    info = dict(url=url)
    username = helper.instagram_get_username_from_url(url)
    if username is None:
        message = f"Can't get username of {url}"
        return None, {"message": message, "status_code": 400}
    api_url = f"https://www.instagram.com/{username}/?__a=1"
    data, error = api_pool.request(method="GET", url=api_url, token=False, type="instagram", metadata=1)
    if error is not None:
        return None, error
    try:
        data = data['graphql']['user']
    except Exception:
        message = f"Can't get graphql of {url}"
        return None, {"message": message, "status_code": 400}
    for field, indicators in constant.instagram_indicators.items():
        pointer = data
        for indicator in indicators:
            if pointer.get(indicator):
                pointer = pointer[indicator]
                info[field] = pointer
            else:
                break
    return info, None

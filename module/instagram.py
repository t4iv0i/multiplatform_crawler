from app import api_pool


def get_info(username, field_info):
    info = dict(username=username)
    api_url = f"https://www.instagram.com/{username}/?__a=1"
    data, error = api_pool.request(url=api_url, domain="instagram", method="GET", proxy=False, cookie=False)
    if error is not None:
        return None, error
    try:
        data = data['graphql']['user']
    except Exception as e:
        message = f"Can't get graphql of {username}.\nDetail: {str(e)}"
        return None, {"message": message, "status_code": 400}
    for field in field_info:
        indicators = field_info[field].get("indicators")
        if indicators is None:
            continue
        pointer = data
        for indicator in indicators:
            if pointer.get(indicator):
                pointer = pointer[indicator]
            else:
                break
        info[field] = pointer
    return info, None

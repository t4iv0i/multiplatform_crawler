from app import api_pool


def get_info(username, field_info):
    info = dict(username=username)
    api_url = f"https://www.instagram.com/{username}/?__a=1"
    data, error = api_pool.request(url=api_url, typ3="instagram", proxy=False)
    if error is not None:
        return None, error
    try:
        data = data['graphql']['user']
    except Exception:
        message = f"Can't get graphql of {username}"
        return None, {"message": message, "status_code": 400}
    for field in field_info:
        indicators = field_info[field].get("indicators")
        if indicators is None:
            continue
        pointer = data
        for indicator in indicators:
            if pointer.get(indicator):
                pointer = pointer[indicator]
                info[field] = pointer
            else:
                break
    return info, None

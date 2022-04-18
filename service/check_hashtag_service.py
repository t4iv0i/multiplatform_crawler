from module import facebook, instagram, tiktok, youtube
from module import helper
from app import manager


def check_hashtag(link, duration, hashtag):
    url = helper.correct_link(link)
    if 'facebook.com' in url:
        return check_hashtag_facebook(url, duration, hashtag)
    elif 'tiktok.com' in url:
        return check_hashtag_tiktok(url, duration, hashtag)
    elif 'instagram.com' in url:
        return check_hashtag_instagram(url, duration, hashtag)
    elif 'youtube.com' in url:
        return check_hashtag_youtube(url, duration, hashtag)
    else:
        return None, {"message": "Current site is not supported"}


def check_hashtag_facebook(url, duration, hashtag):
    chrome = manager.get_active_crawler()
    if chrome is None:
        return None, {"message": f"All crawler are busy. Try again later"}
    from_datetime, to_datetime = helper.parse_duration(duration)
    articles = facebook.get_article(chrome=chrome, url=url, from_datetime=from_datetime, to_datetime=to_datetime)
    manager.set_active_crawler(chrome)
    print(len(articles))
    for article in articles:
        if article.get('hashtag') and hashtag in article['hashtag']:
            return {"message": "chuẩn rồi"}, None
        print(article['content'])
        for content in article['content']:
            if hashtag in content:
                return {"message": "chuẩn rồi"}, None
    return {"message": "chưa thấy"}, None


def check_hashtag_tiktok(url, duration, hashtag):
    return None, {"message": f"All crawler are busy. Try again later"}


def check_hashtag_instagram(url, duration, hashtag):
    return None, {"message": f"All crawler are busy. Try again later"}


def check_hashtag_youtube(url, duration, hashtag):
    return None, {"message": f"All crawler are busy. Try again later"}
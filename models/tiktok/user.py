from models.template import *


class User(Template):
    meta = {
        'db_alias': 'tiktok',
        'collection': 'User'
    }
    index = {
        "id": None
    }
    fields = {
        "id": {"type": "string"},
        "name": {"type": "string", "xpath": "/html/body//h1[contains(@data-e2e, 'user-subtitle') or contains(@class, 'share-sub-title')]"},
        "username": {"type": "string", "xpath": "/html/body//h2[contains(@data-e2e, 'user-title') or contains(@class, 'share-title')]"},
        "follower_count": {"type": "int", "xpath": "/html/body//strong[contains(@title, 'Follower') or contains(@data-e2e, 'followers-count')]"},
        "following_count": {"type": "int", "xpath": "/html/body//div/strong[contains(@title, 'Following') or contains(@title, 'Đang Follow') or contains(@data-e2e, 'following-count')]"},
        "like_count": {"type": "int", "xpath": "/html/body//strong[contains(@title, 'Likes') or contains(@title, 'Thích') or contains(@data-e2e, 'likes-count')]"},
        "description": {"type": "string", "xpath": "/html/body//h2[contains(@class, 'share-desc') or contains(@data-e2e, 'user-bio')]"},
        "share_link": {"type": "string", "xpath": "/html/body//div[contains(@class, 'share-links')]/a"}
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(data=data)


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
        "name": {"type": "string"},
        "username": {"type": "string"},
        "follower": {"type": "int"},
        "following": {"type": "int"},
        "like": {"type": "int"},
        "description": {"type": "string"},
        "share_link": {"type": "string"}
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(data=data)


from models.template import *


class User(Template):
    meta = {
        'db_alias': 'youtube',
        'collection': 'User'
    }
    index = {
        "id": None
    }
    fields = {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "follower": {"type": "int"},
        "view": {"type": "int"},
        "description": {"type": "string"},
        "detail": {"type": "string"},
        "date_joined": {"type": "datetime"}
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(data=data)
from models.template import *


class User(Template):
    meta = {
        'db_alias': 'instagram',
        'collection': 'Role'
    }
    index = {
        "id": None
    }
    fields = {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "post": {"type": "int"},
        "follower": {"type": "int"},
        "following": {"type": "int"},
        "description": {"type": "string"}
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(data=data)

from models.template import *


class User(Template):
    meta = {
        'db_alias': 'account',
        'collection': 'Role'
    }
    fields = {
        "username": {"type": "str"},
        "hash_password": {"type": "str"},
        "roles": {"type": "list"},
        "status": {"type": "str"},
    }
    connections = {
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)
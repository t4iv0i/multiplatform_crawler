from models.template import *


class Role(Template):
    meta = {
        'db_alias': 'account',
        'collection': 'User'
    }
    fields = {
        "database": {"type": "str"},
        "collection": {"type": "list"},
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)
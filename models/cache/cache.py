from models.template import *


class Cache(Template):
    meta = {
        'db_alias': 'cache',
        'collection': 'Cache'
    }
    index = {"uuid": None, "username": None}
    fields = {
        "uuid": {"type": "str"},
        "username": {"type": "str"},
        "params": {"type": "dict"},
        "data": {"type": "dict"},
        "status": {"type": "str"}
    }
    connections = {

    }
    system = {
        "created_time": {"type": "datetime"},
        "updated_time": {"type": "datetime"}
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)



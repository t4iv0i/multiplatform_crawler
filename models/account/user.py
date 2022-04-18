from models.template import *


class User(Template):
    meta = {
        'db_alias': 'account',
        'collection': 'Role'
    }
    fields = {
        "username": (str, True),
        "hash_password": (str, True),
        "status": (str, True),
    }
    edges = {
        "roles": (list, True),
    }
    system = {
        "created_time": (datetime, True),
        "updated_time": (datetime, True)
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(fields=self.fields, edges=self.edges, system=self.system, data=data)

from models.template import *


class Video(Template):
    meta = {
        'db_alias': 'youtube',
        'collection': 'Video'
    }
    fields = {
        "id": (str, True)
    }
    connections = {

    }
    system = {
        "created_time": (datetime, True),
        "updated_time": (datetime, True)
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(fields=self.fields, connections=self.connections, system=self.system, data=data)


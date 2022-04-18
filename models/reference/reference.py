from models.template import Template


class Reference(Template):
    meta = {
        "db_alias": "reference",
        "collection": "Reference"
    }
    index = {

    }
    connections = {
        "source": {"type": "Link"},
        "destination": {"type": "Link"},
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)
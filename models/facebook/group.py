from models.template import Template


class Group(Template):
    meta = {
        "db_alias": "facebook",
        "collection": "Group"
    }
    index = {
        "id": None
    }
    fields = {
              "id": {"type": "numeric string", "version": "v13.0", "param": "id"},
              "created_time": {"type": "datetime", "version": "v13.0", "param": "created_time"},
              "description": {"type": "string", "version": "v13.0", "param": "description"},
              "email": {"type": "string", "version": "v13.0", "param": "email"},
              "link": {"type": "string", "version": "v13.0", "param": "link"},
              "member_count": {"type": "unsigned int32", "version": "v13.0", "param": "member_count"},
              "member_request_count": {"type": "unsigned int32", "version": "v13.0", "param": "member_request_count"},
              "name": {"type": "string", "version": "v13.0", "param": "name"},
              "subdomain": {"type": "string", "version": "v13.0", "param": "subdomain"},
              "updated_time": {"type": "datetime", "version": "v13.0", "param": "updated_time"},
    }
    connections = {}

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)

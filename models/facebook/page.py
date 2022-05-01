from models.template import Template


class Page(Template):
    meta = {
        "db_alias": "facebook",
        "collection": "Page"
    }
    index = {
        "id": None
    }
    fields = {
              "id": {"type": "numeric string", "version": "v13.0", "param": "id"},
              "about": {"type": "string", "version": "v13.0", "param": "about"},
              "bio": {"type": "string", "version": "v13.0", "param": "bio"},
              "birthday": {"type": "string", "version": "v13.0", "param": "birthday"},
              "category": {"type": "string", "version": "v13.0", "param": "category"},
              "category_list": {"type": "list<pagecategory>", "version": "v13.0", "param": "category_list"},
              "description": {"type": "string", "version": "v13.0", "param": "description"},
              "engagement": {"type": "engagement", "version": "v13.0", "param": "engagement"},
              "fan_count": {"type": "unsigned int32", "version": "v13.0", "param": "fan_count"},
              "followers_count": {"type": "unsigned int32", "version": "v13.0", "param": "followers_count"},
              "general_info": {"type": "string", "version": "v13.0", "param": "general_info"},
              "hometown": {"type": "string", "version": "v13.0", "param": "hometown"},
              "link": {"type": "string", "version": "v13.0", "param": "link"},
              "location": {"type": "location", "version": "v13.0", "param": "location"},
              "members": {"type": "string", "version": "v13.0", "param": "members"},
              "name": {"type": "string", "version": "v13.0", "param": "name"},
              "personal_info": {"type": "string", "version": "v13.0", "param": "personal_info"},
              "phone": {"type": "string", "version": "v13.0", "param": "phone"},
              "place_type": {"type": "enum", "version": "v13.0", "param": "place_type"},
              "price_range": {"type": "string", "version": "v13.0", "param": "price_range"},
              "username": {"type": "string", "version": "v13.0", "param": "username"},
              "website": {"type": "string", "version": "v13.0", "param": "website"},
              "were_here_count": {"type": "unsigned int32", "version": "v13.0", "param": "were_here_count"},
    }
    connections = {}

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)

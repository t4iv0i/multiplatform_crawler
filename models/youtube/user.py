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
        "name": {"type": "string", "xpath": "//*[@id='text-container']"},
        "subscriber_count": {"type": "int", "xpath": "//*[@id='subscriber-count']"},
        "view_count": {"type": "int", "xpath": "*[@id='right-column']/yt-formatted-string[3]"},
        "description": {"type": "string", "xpath": "//*[@id='description-container']/yt-formatted-string[2]"},
        "detail": {"type": "string", "xpath": "//*[@id='details-container']/table"},
        "date_joined": {"type": "datetime", "xpath": "//*[@id='right-column']/yt-formatted-string[2]"}
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(data=data)
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
        "id": {"type": "string", "indicators": ["id"]},
        "name": {"type": "string", "indicators": ["full_name"]},
        "username": {"type": "string", "indicators": ["graphql", "user", "username"]},
        "post_count": {"type": "int", "indicators": ["edge_owner_to_timeline_media", "count"]},
        "follower_count": {"type": "int", "indicators": ["edge_followed_by", "count"]},
        "following_count": {"type": "int", "indicators": ["edge_follow", "count"]},
        "description": {"type": "string", "indicators": ["biography"]}
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        super().__init__(data=data)

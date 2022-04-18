from models.template import Template


class User(Template):
    meta = {
        "db_alias": "facebook",
        "collection": "User"
    }
    index = {
        "id": None
    }
    fields = {"created_time": {"type": "datetime", "version": "v13.0", "param": "created_time"},
              "username": {"type": "string", "version": "v13.0", "param": "username"},
              "about": {"type": "string", "version": "v13.0", "param": "about"},
              "id": {"type": "numeric string", "version": "v13.0", "param": "id"},
              "age_range": {"type": "agerange", "version": "v13.0", "param": "age_range"},
              "birthday": {"type": "string", "version": "v13.0", "param": "birthday"},
              "education": {"type": "list<educationexperience>", "version": "v13.0", "param": "education"},
              "email": {"type": "string", "version": "v13.0", "param": "email"},
              "first_name": {"type": "string", "version": "v13.0", "param": "first_name"},
              "gender": {"type": "string", "version": "v13.0", "param": "gender"},
              "hometown": {"type": "page", "version": "v13.0", "param": "hometown"},
              "inspirational_people": {"type": "list<experience>", "version": "v13.0", "param": "inspirational_people"},
              "interested_in": {"type": "list<string>", "version": "v13.0", "param": "interested_in"},
              "languages": {"type": "list<experience>", "version": "v13.0", "param": "languages"},
              "last_name": {"type": "string", "version": "v13.0", "param": "last_name"},
              "link": {"type": "string", "version": "v13.0", "param": "link"},
              "middle_name": {"type": "string", "version": "v13.0", "param": "middle_name"},
              "name": {"type": "string", "version": "v13.0", "param": "name"},
              "quotes": {"type": "string", "version": "v13.0", "param": "quotes"},
              "relationship_status": {"type": "string", "version": "v13.0", "param": "relationship_status"},
              "short_name": {"type": "string", "version": "v13.0", "param": "short_name"},
              "website": {"type": "string", "version": "v13.0", "param": "website"},
              "work": {"type": "list<workexperience>", "version": "v13.0", "param": "work"}}
    connections = {"subscribers": {"version": "v1.0", "param": "subscribers", "type": "list<User,Page,Group>"},
                   "feed": {"version": "v13.0", "param": "feed", "type": "list<Link>"},
                   "friends": {"version": "v13.0", "param": "friends", "type": "list<Link>"},
                   "likes": {"version": "v13.0", "param": "likes", "type": "list<Link>"},
                   "photos": {"version": "v13.0", "param": "photos", "type": "list<Link>"},
                   "picture": {"version": "v13.0", "param": "picture", "type": "list<Link>"},
                   "posts": {"version": "v13.0", "param": "posts", "type": "list<Post>"},
                   "videos": {"version": "v13.0", "param": "videos", "type": "list<Link>"}}

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)

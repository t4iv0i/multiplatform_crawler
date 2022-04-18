from models.template import Template


class Album(Template):
    meta = {
        "db_alias": "facebook",
        "collection": "Album"
    }
    index = {
        "id": None
    }
    fields = {
        "id": {
            "type": "numeric string",
            "version": "v1.0",
            "param": "id"},
        "can_upload": {
            "type": "bool",
            "version": "v1.0",
            "param": "can_upload"},
        "count": {
            "type": "unsigned int32",
            "version": "v1.0",
            "param": "count"},
        "cover_photo": {
            "type": "numeric string",
            "version": "v1.0",
            "param": "cover_photo"},
        "created_time": {
            "type": "datetime",
            "version": "v1.0",
            "param": "created_time"},
        "description": {
            "type": "string",
            "version": "v1.0",
            "param": "description"},
        "from": {
            "type": "user|page",
            "version": "v1.0",
            "param": "from"},
        "link": {
            "type": "token with structure: url",
            "version": "v1.0",
            "param": "link"},
        "location": {
            "type": "string",
            "version": "v1.0",
            "param": "location"},
        "name": {
            "type": "string",
            "version": "v1.0",
            "param": "name"},
        "place": {
            "version": "v1.0",
            "param": "place"},
        "privacy": {
            "type": "string",
            "version": "v1.0",
            "param": "privacy"},
        "type": {
            "type": "string",
            "version": "v1.0",
            "param": "type"},
        "updated_time": {
            "type": "datetime",
            "version": "v1.0",
            "param": "updated_time"},
        "backdated_time": {
            "type": "datetime",
            "version": "v2.2",
            "param": "backdated_time"},
        "backdated_time_granularity": {
            "type": "enum",
            "version": "v2.2",
            "param": "backdated_time_granularity"},
        "event": {
            "type": "event",
            "version": "v2.3",
            "param": "event"}
    }
    connections = {
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)

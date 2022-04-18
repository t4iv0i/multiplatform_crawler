from models.template import Template


class Video(Template):
    meta = {
        "db_alias": "facebook",
        "collection": "Video"
    }
    fields = {
        "ad_breaks": {
            "type": "list<integer>",
            "version": "v1.0",
            "param": "ad_breaks"},
        "backdated_time": {
            "type": "datetime",
            "version": "v1.0",
            "param": "backdated_time"},
        "id": {
            "type": "numeric string",
            "version": "v1.0",
            "param": "id"},
        "backdated_time_granularity": {
            "type": "enum",
            "version": "v1.0",
            "param": "backdated_time_granularity"},
        "created_time": {
            "type": "datetime",
            "version": "v1.0",
            "param": "created_time"},
        "custom_labels": {
            "type": "list<string>",
            "version": "v1.0",
            "param": "custom_labels"},
        "description": {
            "type": "string",
            "version": "v1.0",
            "param": "description"},
        "embed_html": {
            "type": "iframe_with_src",
            "version": "v1.0",
            "param": "embed_html"},
        "format": {
            "type": "list<videoformat>",
            "version": "v1.0",
            "param": "format"},
        "from": {
            "type": "user|page",
            "version": "v1.0",
            "param": "from"},
        "icon": {
            "type": "string",
            "version": "v1.0",
            "param": "icon"},
        "is_crosspost_video": {
            "type": "bool",
            "version": "v1.0",
            "param": "is_crosspost_video"},
        "is_instagram_eligible": {
            "type": "bool",
            "version": "v1.0",
            "param": "is_instagram_eligible"},
        "length": {
            "type": "float",
            "version": "v1.0",
            "param": "length"},
        "permalink_url": {
            "type": "uri",
            "version": "v1.0",
            "param": "permalink_url"},
        "place": {
            "version": "v1.0",
            "param": "place"},
        "premiere_living_room_status": {
            "type": "enum",
            "version": "v1.0",
            "param": "premiere_living_room_status"},
        "privacy": {
            "type": "privacy",
            "version": "v1.0",
            "param": "privacy"},
        "source": {
            "type": "string",
            "version": "v1.0",
            "param": "source"},
        "status": {
            "type": "videostatus",
            "version": "v1.0",
            "param": "status"},
        "universal_video_id": {
            "type": "string",
            "version": "v1.0",
            "param": "universal_video_id"},
        "updated_time": {
            "type": "datetime",
            "version": "v1.0",
            "param": "updated_time"},
        "event": {
            "type": "event",
            "version": "v2.3",
            "param": "event"},
        "published": {
            "type": "bool",
            "version": "v2.3",
            "param": "published"},
        "scheduled_publish_time": {
            "type": "datetime",
            "version": "v2.3",
            "param": "scheduled_publish_time"},
        "content_category": {
            "type": "enum",
            "version": "v2.4",
            "param": "content_category"},
        "embeddable": {
            "type": "bool",
            "version": "v2.4",
            "param": "embeddable"},
        "title": {
            "type": "string",
            "version": "v2.5",
            "param": "title"},
        "content_tags": {
            "type": "list<numeric string>",
            "version": "v2.6",
            "param": "content_tags"},
        "is_crossposting_eligible": {
            "type": "bool",
            "version": "v2.6",
            "param": "is_crossposting_eligible"},
        "live_status": {
            "type": "enum",
            "version": "v2.6",
            "param": "live_status"},
        "is_episode": {
            "type": "bool",
            "version": "v3.0",
            "param": "is_episode"},
        "post_views": {
            "type": "unsigned int32",
            "version": "v12.0",
            "param": "post_views"},
        "views": {
            "type": "unsigned int32",
            "version": "v12.0",
            "param": "views"}
    }
    index = {
        "id": None
    }
    connections = {
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)

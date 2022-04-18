from models.template import Template


class Event(Template):
    meta = {
        "db_alias": "facebook",
        "collection": "Event"
    }
    index = {
        "id": None
    }
    fields = {
        "id": {
            "type": "numeric string",
            "version": "v1.0",
            "param": "id"},
        "cover": {
            "type": "coverphoto",
            "version": "v1.0",
            "param": "cover"},
        "created_time": {
            "type": "datetime",
            "version": "v1.0",
            "param": "created_time"},
        "description": {
            "type": "string",
            "version": "v1.0",
            "param": "description"},
        "discount_code_enabled": {
            "type": "bool",
            "version": "v1.0",
            "param": "discount_code_enabled"},
        "end_time": {
            "type": "string",
            "version": "v1.0",
            "param": "end_time"},
        "event_times": {
            "type": "list<childevent>",
            "version": "v1.0",
            "param": "event_times"},
        "is_canceled": {
            "type": "bool",
            "version": "v1.0",
            "param": "is_canceled"},
        "is_date_only": {
            "type": "bool",
            "version": "v1.0",
            "param": "is_date_only"},
        "is_online": {
            "type": "bool",
            "version": "v1.0",
            "param": "is_online"},
        "is_page_owned": {
            "type": "bool",
            "version": "v1.0",
            "param": "is_page_owned"},
        "is_pay_to_access": {
            "type": "bool",
            "version": "v1.0",
            "param": "is_pay_to_access"},
        "location": {
            "type": "string",
            "version": "v1.0",
            "param": "location"},
        "name": {
            "type": "string",
            "version": "v1.0",
            "param": "name"},
        "online_event_format": {
            "type": "enum {messenger_room, third_party, fb_live, other, none}",
            "version": "v1.0",
            "param": "online_event_format"},
        "online_event_third_party_url": {
            "type": "string",
            "version": "v1.0",
            "param": "online_event_third_party_url"},
        "owner": {
            "version": "v1.0",
            "param": "owner"},
        "parent_group": {
            "type": "group",
            "version": "v1.0",
            "param": "parent_group"},
        "privacy": {
            "type": "string",
            "version": "v1.0",
            "param": "privacy"},
        "scheduled_publish_time": {
            "type": "string",
            "version": "v1.0",
            "param": "scheduled_publish_time"},
        "start_time": {
            "type": "string",
            "version": "v1.0",
            "param": "start_time"},
        "ticket_uri": {
            "type": "string",
            "version": "v1.0",
            "param": "ticket_uri"},
        "ticket_uri_start_sales_time": {
            "type": "string",
            "version": "v1.0",
            "param": "ticket_uri_start_sales_time"},
        "ticketing_privacy_uri": {
            "type": "string",
            "version": "v1.0",
            "param": "ticketing_privacy_uri"},
        "ticketing_terms_uri": {
            "type": "string",
            "version": "v1.0",
            "param": "ticketing_terms_uri"},
        "timezone": {
            "type": "enum",
            "version": "v1.0",
            "param": "timezone"},
        "updated_time": {
            "type": "datetime",
            "version": "v1.0",
            "param": "updated_time"},
        "venue": {
            "type": "location",
            "version": "v1.0",
            "param": "venue"},
        "attending_count": {
            "type": "int32",
            "version": "v2.1",
            "param": "attending_count"},
        "declined_count": {
            "type": "int32",
            "version": "v2.1",
            "param": "declined_count"},
        "interested_count": {
            "type": "int32",
            "version": "v2.1",
            "param": "interested_count"},
        "invited_count": {
            "type": "int32",
            "version": "v2.1",
            "param": "invited_count"},
        "maybe_count": {
            "type": "int32",
            "version": "v2.1",
            "param": "maybe_count"},
        "noreply_count": {
            "type": "int32",
            "version": "v2.1",
            "param": "noreply_count"},
        "place": {
            "type": "place",
            "version": "v2.3",
            "param": "place"},
        "category": {
            "type": "enum",
            "version": "v2.4",
            "param": "category"},
        "type": {
            "type": "enum {private, public, group, community, friends, work_company}",
            "version": "v2.4",
            "param": "type"}
    }
    connections = {

    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)

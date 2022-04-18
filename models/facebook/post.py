from models.template import Template


class Post(Template):
    meta = {
        "db_alias": "facebook",
        "collection": "Post"
    }
    index = {
        "id": None
    }
    fields = {"implicit_place": {"type": "place", "version": "v12.0", "param": "implicit_place"},
              "actions": {"type": "list", "version": "v12.0", "param": "actions"},
              "admin_creator": {"type": "businessuser|user|application", "version": "v12.0", "param": "admin_creator"},
              "allowed_advertising_objectives": {"type": "list<string>", "version": "v12.0",
                                                 "param": "allowed_advertising_objectives"},
              "app_installs_eligibility": {"type": "bool", "version": "v12.0", "param": "app_installs_eligibility"},
              "application": {"type": "application", "version": "v12.0", "param": "application"},
              "backdated_time": {"type": "datetime", "version": "v12.0", "param": "backdated_time"},
              "call_to_action": {"type": "list", "version": "v12.0",
                                 "param": "call_to_action"},
              "caption": {"type": "string", "version": "v12.0", "param": "caption"},
              "child_attachments": {"type": "list", "version": "v12.0", "param": "child_attachments"},
              "id": {"type": "token with structure: post id", "version": "v12.0", "param": "id"},
              "comments_mirroring_domain": {"type": "string", "version": "v12.0", "param": "comments_mirroring_domain"},
              "coordinates": {
                  "type": "list",
                  "version": "v12.0", "param": "coordinates"},
              "created_time": {"type": "datetime", "version": "v12.0", "param": "created_time"},
              "delivery_growth_optimizations": {"type": "list<enum>", "version": "v12.0",
                                                "param": "delivery_growth_optimizations"},
              "description": {"type": "string", "version": "v12.0", "param": "description"},
              "event": {"type": "event", "version": "v12.0", "param": "event"},
              "expanded_height": {"type": "unsigned int32", "version": "v12.0", "param": "expanded_height"},
              "expanded_width": {"type": "unsigned int32", "version": "v12.0", "param": "expanded_width"},
              "feed_targeting": {
                  "type": "list",
                  "version": "v12.0", "param": "feed_targeting"},
              "from": {"type": "user|page", "version": "v12.0", "param": "from"},
              "full_picture": {"type": "string", "version": "v12.0", "param": "full_picture"},
              "height": {"type": "unsigned int32", "version": "v12.0", "param": "height"},
              "icon": {"type": "string", "version": "v12.0", "param": "icon"},
              "instagram_eligibility": {"type": "enum", "version": "v12.0", "param": "instagram_eligibility"},
              "is_app_share": {"type": "bool", "version": "v12.0", "param": "is_app_share"},
              "is_eligible_for_promotion": {"type": "bool", "version": "v12.0", "param": "is_eligible_for_promotion"},
              "is_expired": {"type": "bool", "version": "v12.0", "param": "is_expired"},
              "is_hidden": {"type": "bool", "version": "v12.0", "param": "is_hidden"},
              "is_instagram_eligible": {"type": "bool", "version": "v12.0", "param": "is_instagram_eligible"},
              "is_popular": {"type": "bool", "version": "v12.0", "param": "is_popular"},
              "is_published": {"type": "bool", "version": "v12.0", "param": "is_published"},
              "is_spherical": {"type": "bool", "version": "v12.0", "param": "is_spherical"},
              "link": {"type": "uri", "version": "v12.0", "param": "link"},
              "live_video_eligibility": {"type": "list<enum>", "version": "v12.0", "param": "live_video_eligibility"},
              "message": {"type": "string", "version": "v12.0", "param": "message"},
              "message_tags": {"type": "list", "version": "v12.0", "param": "message_tags"},
              "multi_share_end_card": {"type": "bool", "version": "v12.0", "param": "multi_share_end_card"},
              "multi_share_optimized": {"type": "bool", "version": "v12.0", "param": "multi_share_optimized"},
              "name": {"type": "string", "version": "v12.0", "param": "name"},
              "object_id": {"type": "string", "version": "v12.0", "param": "object_id"},
              "parent_id": {"type": "token with structure: post id", "version": "v12.0", "param": "parent_id"},
              "permalink_url": {"type": "uri", "version": "v12.0", "param": "permalink_url"},
              "place": {"type": "place", "version": "v12.0", "param": "place"},
              "privacy": {"type": "privacy", "version": "v12.0", "param": "privacy"},
              "promotable_id": {"type": "token with structure: post id", "version": "v12.0", "param": "promotable_id"},
              "promotion_status": {"type": "string", "version": "v12.0", "param": "promotion_status"},
              "properties": {"type": "list", "version": "v12.0", "param": "properties"},
              "scheduled_publish_time": {"type": "float", "version": "v12.0", "param": "scheduled_publish_time"},
              "shares": {"type": "list", "version": "v12.0", "param": "shares"},
              "source": {"type": "string", "version": "v12.0", "param": "source"},
              "status_type": {"type": "string", "version": "v12.0", "param": "status_type"},
              "story": {"type": "string", "version": "v12.0", "param": "story"},
              "story_tags": {"type": "list", "version": "v12.0", "param": "story_tags"},
              "subscribed": {"type": "bool", "version": "v12.0", "param": "subscribed"},
              "target": {"type": "profile", "version": "v12.0", "param": "target"}, "targeting": {
            "type": "list",
            "version": "v12.0", "param": "targeting"},
              "timeline_visibility": {"type": "string", "version": "v12.0", "param": "timeline_visibility"},
              "type": {"type": "string", "version": "v12.0", "param": "type"},
              "updated_time": {"type": "datetime", "version": "v12.0", "param": "updated_time"},
              "via": {"type": "user|page", "version": "v12.0", "param": "via"},
              "video_buying_eligibility": {"type": "list<enum>", "version": "v12.0",
                                           "param": "video_buying_eligibility"},
              "width": {"type": "unsigned int32", "version": "v12.0", "param": "width"},
              "will_be_autocropped_when_deliver_to_instagram": {"type": "bool", "version": "v12.0",
                                                                "param": "will_be_autocropped_when_deliver_to_instagram"}}
    connections = {"attachments": {"version": "v12.0", "param": "attachments", "type": "list<Link>"},
                   "comments": {"version": "v12.0", "param": "comments", "type": "list<Link>"},
                   "dynamic_posts": {"version": "v12.0", "param": "dynamic_posts", "type": "list<Link>"},
                   "reactions": {"version": "v12.0", "param": "reactions", "type": "list<Link>"},
                   "sharedposts": {"version": "v12.0", "param": "sharedposts", "type": "list<Link>"}}

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database=cls.meta["db_alias"], collection=cls.meta["collection"])

    def __init__(self, data):
        if data and type(data) == dict:
            super().__init__(data=data)
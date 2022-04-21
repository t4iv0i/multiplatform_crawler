from constant import constant
from module import facebook, instagram, tiktok,  youtube, mongo, helper
from models import Model
from service import mongo_service


def get_facebook_info(params):
    command = params["command"]
    if command == "create":
        url = params["url"]
        node_info, error = facebook.get_facebook_identity(url)
        if error is not None:
            return None, error
        database, collection, node_id = "facebook", node_info.pop('collection'), node_info['id']
        params.update({"collection": collection})
        model = Model.get(database=database, collection=collection)
        fields = params.get("fields", [])
        if not fields:
            field_info = model.fields
            fields = list(model.fields.keys())
        else:
            for field in ["id", "about"]:
                if field not in fields:
                   fields.append(field)
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        node_data, error = facebook.get_node_info(uid=node_id, field_info=field_info)
        if error is not None:
            yield None, error
            return
        node_data.update(node_info)
        hashtag = helper.normalize_hashtag(params["hashtag"])
        if node_data.get("about") and hashtag.upper() in node_data["about"].upper():
            if node_data.get("followers_count") and node_data["followers_count"] >= constant.REQUIRED_FOLLOWER:
                node_data["is_verified"] = True
        else:
            node_data["is_verified"] = False
        return node_data, None
    elif command == "update":
        database = params["database"]
        collection = params["collection"]
        model = Model.get(database=database, collection=collection)
        filters = params.get("filters")
        fields = params.get("fields")
        if not fields:
            field_info = model.fields
            fields = list(model.fields.keys())
        else:
            if "id" not in fields:
                fields.append("id")
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        result, error = mongo.client_read(database=database, collection=collection, filters=filters, fields=fields)
        if error is not None:
            message = f"Cant get user index. Detail: {error['message']}"
            return None, {"message": message, "status_code": 400}
        for index in range(len(result)):
            record = model(result[index]).to_str()
            node_data, error = facebook.get_node_info(uid=record["id"], field_info=field_info)
            if error is not None:
                return None, error
            print(node_data)
            result[index] = helper.recursive_update(source=node_data, dest=record)
        return result, None


def get_instagram_info(params):
    command = params["command"]
    if command == "create":
        url, database, collection = params["url"], "instagram", "User"
        username = helper.instagram_get_username_from_url(url)
        if username is None:
            message = f"Can't get username of {url}"
            return None, {"message": message, "status_code": 400}
        model = Model.get(database=database, collection=collection)
        fields = params.get("fields", [])
        if not fields:
            field_info = model.fields
            fields = list(model.fields.keys())
        else:
            for field in ["id", "description"]:
                if field not in fields:
                    fields.append(field)
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        node_data, error = instagram.get_info(username=username, field_info=field_info)
        if error is not None:
            return None, error
        node_data.update({"type": "instagram", "is_verified": False})
        hashtag_upper = helper.normalize_hashtag(params["hashtag"])
        if node_data.get('description') and hashtag_upper in node_data['description'].upper():
            if node_data["follower"] >= constant.REQUIRED_FOLLOWER:
                node_data["is_verified"] = True
        return node_data, None
    elif command == "update":
        database = params["database"]
        collection = params["collection"]
        model = Model.get(database=database, collection=collection)
        filters = params.get("filters")
        fields = params.get("fields", [])
        if not fields:
            field_info = model.fields
            fields = field_info.keys()
        else:
            for field in ["id", "username"]:
                if field not in fields:
                    fields.append(field)
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        result, error = mongo.client_read(database=database, collection=collection, filters=filters, fields=fields)
        if error is not None:
            message = f"Cant get user index. Detail: {error['message']}"
            return None, {"message": message, "status_code": 400}
        for index in range(len(result)):
            record = model(result[index]).to_str()
            node_data, error = instagram.get_info(username=record["username"], field_info=field_info)
            if error is not None:
                return None, error
            print(node_data)
            result[index] = helper.recursive_update(source=node_data, dest=record)
        return result, None


def get_youtube_info(params):
    command = params["command"]
    if command == "create":
        url = params["url"]
        channel_id, error = youtube.get_channel_id(url)
        if error is not None:
            return None, error
        database, collection = "youtube", "User"
        model = Model.get(database=database, collection=collection)
        fields = params.get("fields", [])
        if not fields:
            field_info = model.fields
            fields = list(model.fields.keys())
        else:
            for field in ["id", "description"]:
                if field not in fields:
                    fields.append(field)
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        node_data, error = youtube.get_info(url=url, field_info=field_info)
        if error is not None:
            return None, error
        node_data["is_verified"] = False
        hashtag_upper = helper.normalize_hashtag(params["hashtag"])
        if node_data.get('description') and hashtag_upper in node_data['description'].upper():
            if node_data["follower"] >= constant.REQUIRED_FOLLOWER:
                node_data["is_verified"] = True
        return node_data, None
    elif command == "update":
        database = params["database"]
        collection = params["collection"]
        filters = params.get("filters")
        model = Model.get(database=database, collection=collection)
        fields = params.get("fields", [])
        if not fields:
            field_info = model.fields
            fields = list(model.fields.keys())
        else:
            for field in ["id", "url"]:
                if field not in fields:
                    fields.append(field)
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        result, error = mongo.client_read(database=database, collection=collection, filters=filters, fields=fields)
        if error is not None:
            message = f"Cant get user index. Detail: {error['message']}"
            return None, {"message": message, "status_code": 400}
        for index in range(len(result)):
            record = model(result[index]).to_str()
            node_data, error = youtube.get_info(url=record["url"], field_info=field_info)
            if error is not None:
                return None, error
            print(node_data)
            result[index] = helper.recursive_update(source=node_data, dest=record)
        return result, None


def get_tiktok_info(params):
    command = params["command"]
    if command == "create":
        url = params["url"]
        user_id, error = tiktok.get_user_id(url)
        if error is not None:
            return None, error
        database, collection = "tiktok", "User"
        model = Model.get(database=database, collection=collection)
        fields = params.get("fields", [])
        if not fields:
            field_info = model.fields
            fields = list(model.fields.keys())
        else:
            for field in ["id", "description"]:
                if field not in fields:
                    fields.append(field)
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        node_data, error = tiktok.get_info(url=url, field_info=field_info)
        if error is not None:
            return None, error
        node_data.update({"id": user_id, "url": url, "is_verified": False})
        hashtag_upper = helper.normalize_hashtag(params["hashtag"])
        if node_data.get('description') and hashtag_upper in node_data['description'].upper():
            if node_data["follower"] >= constant.REQUIRED_FOLLOWER:
                node_data["is_verified"] = True
        return node_data, None
    elif command == "update":
        database = params["database"]
        collection = params["collection"]
        model = Model.get(database=database, collection=collection)
        filters = params.get("filters")
        fields = params.get("fields", [])
        if not fields:
            field_info = model.fields
            fields = list(model.fields.keys())
        else:
            for field in ["id", "url"]:
                if field not in fields:
                    fields.append(field)
            field_info = dict()
            for field in fields:
                field_info[field] = model.fields[field]
        params["fields"] = fields
        result, error = mongo.client_read(database=database, collection=collection, filters=filters, fields=fields)
        if error is not None:
            message = f"Cant get user index. Detail: {error['message']}"
            return None, {"message": message, "status_code": 400}
        for index in range(len(result)):
            record = model(result[index]).to_str()
            node_data, error = tiktok.get_info(url=record["url"], field_info=field_info)
            if error is not None:
                return None, error
            print(node_data)
            result[index] = helper.recursive_update(source=node_data, dest=record)
        return result, None

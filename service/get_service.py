from constant import constant
from module import facebook, instagram, mongo, helper
# tiktok,  youtube
from models import Model
from service import mongo_service


def get_facebook_info(params):
    command = params["command"]
    if command == "create":
        url = params["url"]
        node_info, error = facebook.get_facebook_identity(url)
        print(node_info)
        if error is not None:
            yield None, error
            return
        database, collection, node_id = "facebook", node_info.pop('collection'), node_info['id']
        params.update({"collection": collection})
        model = Model.get(database=database, collection=collection)
        fields = params.get("fields")
        if not fields:
            fields = list(model.fields.keys())
        params["fields"] = fields
        node_data, error = facebook.get_node_info(uid=node_id, field_info=model.fields, fields=fields)
        if error is not None:
            yield None, error
            return
        node_data.update(node_info)
        if node_data.get("about") and node_data.get("followers_count"):
            hashtag = helper.normalize_hashtag(params["hashtag"])
            if hashtag.lower() in node_data["about"].lower() and node_data["followers_count"] >= constant.REQUIRED_FOLLOWER:
                node_data["is_verified"] = True
        else:
            node_data["is_verified"] = False
        yield node_data, None
        username, uuid = params["username"], params["uuid"]
        for connection_params in params.pop("connections", []):
            connection_params.update({"username": username, "uuid": uuid})
            connection_name = connection_params["connection_name"]
            version = model.connections[connection_name]["version"]
            condition = connection_params.get("condition")
            generator = facebook.get_connection_id(uid=node_id, connection=connection_name, version=version, condition=condition)
            limit, condition = next(generator)
            yield limit, condition
            path, index = f"{connection_name}", 0
            for record in generator:
                _collection, error = facebook.get_facebook_collection(uid=record['id'])
                if error is not None:
                    print(error)
                    return
                _id, index = record["id"], index + 1
                connection_data = {"id": node_id, connection_name: {"database": database, "collection": _collection, "id": _id}}
                connection_params.update({"collection": _collection, "path": path + f"[{index}]"})
                yield connection_data, connection_params
        return
    elif command == "update":
        database = params["database"]
        collection = params["collection"]
        filters = params.get("filters")
        fields = params.get("fields").copy()
        for connection_params in params.get("connections", []):
            fields.append(connection_params["connection_name"])
        result, error = mongo.client_read(database=database, collection=collection, filters=filters, fields=fields)
        if error is not None:
            message = f"Cant get user index. Detail: {error['message']}"
            return None, {"message": message, "status_code": 400}
        model = Model.get(database=database, collection=collection)
        for index in range(len(result)):
            record = model(result[index]).to_str()
            node_data, error = facebook.get_info(uid=record["id"], requirement=params)
            if error is not None:
                return None, error
            print(node_data)
            result[index] = helper.recursive_update(source=node_data, dest=record)
        return result, None


def get_instagram_info(params):
    command = params["command"]
    if command == "create":
        url = params["url"]
        info = instagram.get_info_api(url=url)
        info.update({"type": "instagram", "is_verified": False})
        hashtag_upper = helper.normalize_hashtag(params["hashtag"])
        info["hashtag"] = False
        if info.get('description'):
            if hashtag_upper in info['description'].upper():
                info['hashtag'] = True
        if info["hashtag"] and info["follower"] >= constant.REQUIRED_FOLLOWER:
            info["is_verified"] = True
        return info, None
    elif command == "update":
        return None, None

#
# def get_tiktok_info(url, hashtag, from_datetime, to_datetime):
#     info = tiktok.get_info(url=url, hashtag=hashtag,
#                            from_datetime=from_datetime, to_datetime=to_datetime)
#     if type(info) == str:
#         timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
#         crawler.browser.save_screenshot(f"error/{info}_{timestamp}.png")
#         return dict(url=url, type="tiktok", is_verified=False), {"message": info}
#     info.update({"type": "tiktok", "is_verified": False})
#     normalized_info = helper.normalize_info(info, "tiktok")
#     check = 0
#     for field in constant.RESPONSE_MUST_HAVE_FIELDS:
#         if normalized_info.get(field) is not None:
#             check += 1
#     if check == len(constant.RESPONSE_MUST_HAVE_FIELDS):
#         if normalized_info["hashtag"] and normalized_info["follower"] >= constant.REQUIRED_FOLLOWER:
#             normalized_info["is_verified"] = True
#         return normalized_info, None
#     else:
#         return normalized_info, {"message": "Lack of information"}
#
#


#
#
# def get_youtube_info(crawler, url, hashtag, from_datetime, to_datetime):
#     info = youtube.get_info(url=url, hashtag=hashtag,
#                             from_datetime=from_datetime, to_datetime=to_datetime)
#     if type(info) == str:
#         timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
#         crawler.browser.save_screenshot(f"error/{info}_{timestamp}.png")
#         return dict(url=url, type="youtube", is_verified=False), {"message": info}
#     info.update({"type": "youtube", "is_verified": False})
#     normalized_info = helper.normalize_info(info, "youtube")
#     check = 0
#     for field in constant.RESPONSE_MUST_HAVE_FIELDS:
#         if normalized_info.get(field) is not None:
#             check += 1
#     if check == len(constant.RESPONSE_MUST_HAVE_FIELDS):
#         if normalized_info["hashtag"] and normalized_info["follower"] >= constant.REQUIRED_FOLLOWER:
#             normalized_info["is_verified"] = True
#         return normalized_info, None
#     else:
#         return normalized_info, {"message": "Lack of information"}

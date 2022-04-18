from app import api_pool, browser_pool
from constant import constant
from dateutil.parser import parse
from module import helper
from models import Model
from bs4 import BeautifulSoup
import re


def get_facebook_collection(uid):
    graph_url = f"{constant.FACEBOOK_GRAPH_API_URL}/v12.0/{uid}"
    data, error = api_pool.request(method="GET", url=graph_url, token=True, type="facebook", metadata=1)
    if error is not None:
        return None, error
    collection_name = constant.CONVERT_COLLECTION_NAME[data["metadata"]["type"]]
    return collection_name, None


def verify_facebook_id_from_post(uid):
    graph_url = f"{constant.FACEBOOK_GRAPH_API_URL}/v12.0/{uid}/posts"
    data, error = api_pool.request(method="GET", url=graph_url, token=True, type="facebook", fields="id", limit=2)
    if error is not None:
        return None, error
    try:
        post_id = data["data"][0]["id"]
        new_id = post_id.split('_')[0]
    except Exception as e:
        message = f"Cant get posts info of {uid}. Detail: {str(e)}"
        return None, {"message": message, "status_code": 400}
    else:
        return new_id, None


def get_facebook_identity(url):
    result = dict()
    regex = re.findall(f'facebook.+', url)
    mbasic_url = f"https://mbasic.{regex[0]}"
    html, error = api_pool.request(method="GET", url=mbasic_url, type="facebook", token=False)
    if error is not None:
        return None, error
    soup = BeautifulSoup(html, features="html.parser")
    link_list = soup.select("body table tr > td > a[href]")
    index, point = dict(), len(link_list)
    for count in range(len(link_list)):
        point -= 1
        for pattern in constant.facebook_id_patterns:
            regex = re.findall(pattern, link_list[count]['href'])
            if regex:
                if index.get(regex[0]):
                    index[regex[0]] += point
                else:
                    index[regex[0]] = point
    if index:
        index = sorted(index.items(), key=lambda x: x[1], reverse=True)
        print(index)
        result['id'] = index[0][0]
    else:
        return None, {"message": f"Can't find id of {mbasic_url}", "status_code": 400}
    collection_name, error = get_facebook_collection(result['id'])
    if error is not None:
        return None, error
    result['collection'] = collection_name
    if collection_name == "User":
        new_id, error = verify_facebook_id_from_post(result['id'])
        if error is not None:
            return None, error
        if new_id != result['id']:
            new_collection_name, error = get_facebook_collection(new_id)
            if error is not None:
                return None, error
            result['id'] = new_id
            result['collection'] = new_collection_name
        else:
            about = soup.select_one(constant.facebook_about_selector)
            if about:
                result['about'] = about.text
    return result, None


def get_node_info(uid, field_info, fields):
    version_fields = dict()
    for field_name in fields:
        if field_info[field_name].get("param"):
            field = field_info[field_name]["param"]
        else:
            field = field_name
        version = field_info[field_name]["version"]
        if version_fields.get(version):
            version_fields[version].append(field)
        else:
            version_fields[version] = [field]
    data = dict()
    for version, current_fields in version_fields.items():
        url = f"{constant.FACEBOOK_GRAPH_API_URL}/{version}/{uid}"
        info, error = api_pool.request(method="GET", url=url, type="facebook", token=True, fields=current_fields)
        if error is not None:
            message = f"Cant get node info of {uid}: {current_fields}.\nDetail: {error['message']}"
            return data, {"message": message, "status_code": 400}
        for field in info:
            field_data = info[field]
            if type(field_data) == dict:
                if field_data.get("data"):
                    data[field] = field_data["data"]
                    continue
                elif field_data.get("summary"):
                    data[field] = field_data["summary"]["total_count"]
                    continue
            data[field] = field_data
    return data, None


def get_connection_id(uid, connection, version, condition):
    break_flag, break_condition, fields = False, dict(), "id"
    if condition:
        for typ3 in condition:
            if typ3 == "count":
                break_condition[typ3] = int(condition[typ3])
            elif typ3 == "duration":
                break_condition[typ3] = helper.parse_duration(duration=condition[typ3])
                fields = "id,created_time"
    summary_url = f"{constant.FACEBOOK_GRAPH_API_URL}/{version}/{uid}/{connection}?fields=summary.total_count"
    info, error = api_pool.request(method="GET", url=summary_url, token=True, type="facebook")
    if error is not None:
        yield None, error
    # limit =
    next_page = f"{constant.FACEBOOK_GRAPH_API_URL}/{version}/{uid}/{connection}?fields={fields}"
    count = 0
    while True:
        info, error = api_pool.request(method="GET", url=next_page, token=True, type="facebook")
        if error is not None:
            message = f"Cant get graph info of {next_page}.\nDetail: {error['message']}"
            yield None, {"message": message, "status_code": 400}
            return
        for record in info["data"]:
            for _type, _condition in break_condition.items():
                if _type == "count" and count > _condition:
                    return
                elif _type == "duration":
                    last = parse(record["created_time"])
                    if last < _condition:
                        return
            yield record, None
        count += len(info)
        if info.get("paging") and info["paging"].get("next"):
            next_page = info["paging"]["next"]
            if not next_page.startswith(constant.FACEBOOK_GRAPH_API_URL):
                 next_page = constant.FACEBOOK_GRAPH_API_URL + next_page
        else:
            return


# def get_info(uid, requirement):
#     model = Model.get(database="facebook", collection=requirement["collection"])
#     fields = requirement.get("fields")
#     if not fields:
#         fields = list(model.fields.keys())
#     requirement["fields"] = fields
#     node_data, error = get_node_info(uid=uid, field_info=model.fields, fields=fields)
#     if error is not None:
#         return None, error
#
#
#     if requirement.get("connections"):
#         for connection_requirement in requirement["connections"]:
#             connection_name = connection_requirement["connection_name"]
#             version = model.connections[connection_name]["version"]
#             condition = connection_requirement.get("condition")
#             connection_data, error = get_connection_id(uid=uid, connection=connection_name, version=version, condition=condition)
#             if error is not None:
#                 return None, error
#             node_data[connection_name] = list()
#             for record in connection_data:
#                 collection, error = get_facebook_collection(uid=record["id"])
#                 if error is not None:
#                     return None, error
#                 node_data[connection_name].append({"database": "facebook", "collection": collection, "id": record["id"]})
#     return node_data, None
#




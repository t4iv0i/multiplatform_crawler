from app import api_pool
from bs4 import BeautifulSoup
from constant import constant
import re


def get_facebook_collection(uid):
    graph_url = f"{constant.FACEBOOK_GRAPH_API_URL}/v12.0/{uid}"
    data, error = api_pool.request(url=graph_url, type="facebook", method="GET", token=True, proxy=False, params={"metadata": 1})
    if error is not None:
        return None, error
    collection_name = constant.CONVERT_COLLECTION_NAME[data["metadata"]["type"]]
    return collection_name, None


def verify_facebook_id_from_post(uid):
    graph_url = f"{constant.FACEBOOK_GRAPH_API_URL}/v12.0/{uid}/posts"
    data, error = api_pool.request(url=graph_url, type="facebook", method="GET", token=True, proxy=True, params={"fields": "id", "limit": 2})
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
    regex = re.findall(f'facebook.+$', url)
    mbasic_url = f"https://mbasic.{regex[0]}"
    html, error = api_pool.request(url=mbasic_url, type="facebook", method="GET", cookie=True)
    if error is not None:
        return None, error
    soup = BeautifulSoup(html, features="html.parser")
    link_list = soup.select("body table tr > td > a[href]")
    index, point = dict(), len(link_list)
    for count in range(len(link_list)):
        point -= 1
        for pattern in constant.mbasic_facebook_id_patterns:
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
            about = soup.select_one(constant.mbasic_facebook_about_selector)
            if about:
                result['about'] = about.text
    return result, None


def get_node_info(uid, field_info):
    version_fields = dict()
    for field_name in field_info.keys():
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
        fields = ','.join(current_fields)
        info, error = api_pool.request(url=url, type="facebook", method="GET", token=True, proxy=True, params={"fields": fields})
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


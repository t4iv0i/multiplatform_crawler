import re

from module import mongo
from module import helper
from models import Model
from dateutil.parser import parse


def validate_login(data):
    required_fields = ["username", "password"]
    if type(data) != dict:
        return False, {
            "message": f"Data type must be dict",
            "status_code": 400
        }
    if set(required_fields) != set(data):
        return False, {
            "message": f"Missing fields. Required fields are: {required_fields}",
            "status_code": 400
        }
    for field in required_fields:
        if type(data[field]) != str:
            return False, {
                "message": f"{data[field]} must be string",
                "status_code": 400
            }
    else:
        return True, None


def normalize_filter(filters, model):
    normalized_filters = filters.copy()
    fields = model.fields.copy()
    fields.update(model.system)
    for field in filters:
        if fields.get(field):
            if fields[field]["type"] == "datetime":
                _filter = filters[field]
                if type(_filter) == str:
                    try:
                        _filter = parse(_filter)
                    except:
                        return None, {
                            "message": f"Can't parse {field} of filters to datetime",
                            "status_code": 400
                        }
                elif type(_filter) == dict:
                    for operator in _filter.keys():
                        try:
                            _filter[operator] = parse(_filter)
                        except:
                            return None, {
                                "message": f"Can't parse {field} of filters to datetime",
                                "status_code": 400
                            }
                normalized_filters[field] = _filter
        else:
            return None, None
    return normalized_filters, None


def validate_requirements(database, params):
    new_params = params.copy()
    collection = params["collection"]
    model = Model.get(database=database, collection=collection)
    if model is None:
        return None, {
            "message": f"Valid collection are: {Model.get_model_names(database)}",
            "status_code": 400
        }
    filters = params.get("filters")
    if filters is not None:
        if type(filters) != dict:
            return None, {
                "message": "Filters must be dict",
                "status_code": 400
            }
        normalized_filters, error = normalize_filter(filters, model)
        if error is not None:
            return None, error
        if normalized_filters is None:
            return None, None
        new_params["filters"] = normalized_filters
    fields = params.get("fields", [])
    for field in fields:
        if model.fields.get(field) is None:
            return None, {
                "message": f"Field {field} not in {database}.{collection}",
                "status_code": 400
            }
    if "id" not in fields:
        fields.append("id")
    new_params["fields"] = fields
    limit = params.get("limit")
    if limit:
        try:
            new_params["limit"] = int(limit)
        except ValueError:
            return None, {
                "message": f"Field limit is not int",
                "status_code": 400
            }
    connection_params = params.get("connections")
    if connection_params:
        if type(connection_params) != list:
            return None, {
                "message": "Connections must be dict",
                "status_code": 400
            }
        normalized_connection_params, errors = list(), None
        for connection_param in connection_params:
            connection_name = connection_param.get("connection_name")
            if connection_name is None:
                return None, {
                    "message": "Connection params must have connection_name field",
                    "status_code": 400
                }
            if model.connections.get(connection_name) is None:
                return None, {
                    "message": f"Connection {connection_name} not exists on {database}.{collection}",
                    "status_code": 400
            }
            connections = re.findall(r'list<(.+)>', model.connections[connection_name]["type"])
            for connection_collection in connections[0].split(','):
                connection_param["collection"] = connection_collection
                new_connection_param, error = validate_requirements(database, connection_param)
                if error is not None:
                    if errors is None:
                        errors = error
                else:
                    normalized_connection_params.append(new_connection_param)
        if normalized_connection_params == list():
            return None, errors
        new_params["connections"] = normalized_connection_params
    return new_params, None


def validate_post_params(params):
    if type(params) != dict:
        return None, {
            "message": "Params must be dict",
            "status_code": 400
        }
    command = params.get("command")
    if command is None:
        return None, {
            "message": "Params must have command field",
            "status_code": 400
        }
    if command == "create":
        url = params.get("url")
        if url is None:
            return None, {
                "message": "Params must have url field",
                "status_code": 400
            }
        if not url.startswith("https:"):
            return None, {
                "message": "Url must start with https",
                "status_code": 400
            }
        hashtag = params.get("hashtag")
        if hashtag is None:
            return None, {
                "message": "Params must have hashtag field",
                "status_code": 400
            }
        database, normalized_url = helper.normalize_link(params["url"])
        normalized_params = params.copy()
        normalized_params.update(database=database, url=normalized_url)
        return normalized_params, None
    elif command == "update":
        database = params.get("database")
        if database is None:
            return None, {
                "message": "Params must have database field",
                "status_code": 400
            }
        normalized_params, error = validate_requirements(database, params)
        if error is not None:
            return None, error
        return normalized_params, None
    else:
        return None, {
            "message": f"Valid command are: [create, update]",
            "status_code": 400
        }


def validate_get_info(params):
    if type(params) != dict:
        return None, {
            "message": "Params must be dict",
            "status_code": 400
        }
    database = params.get("database")
    if database is None:
        return None, {
            "message": "Params must have database field",
            "status_code": 400
        }
    normalized_params, error = validate_requirements(database, params)
    if error is not None:
        return None, error
    return normalized_params, None


def validate_get_batch_info(params):
    if type(params) != dict:
        return {
            "message": "Params must be dict",
            "status_code": 400
        }
    limit = params.get("limit")
    if limit is None:
        return {
            "message": "Params must have limit field",
            "status_code": 400
        }
    try:
        _ = int(limit)
    except:
        return {
            "message": "Limit field must be integer",
            "status_code": 400
        }
    return None


def validate_post_batch_params(batch_params):
    if type(batch_params) != dict:
        return None, {
            "message": "Params must be dict",
            "status_code": 400
        }
    params = batch_params.get("params")
    if params is None:
        return None, {
            "message": "Params must have params field",
            "status_code": 400
        }
    normalized_params = list()
    for param in params:
        normalized_param, error = validate_post_params(param)
        if error:
            return None, error
        normalized_params.append(normalized_param)
    else:
        return normalized_params, None


def validate_permission(params):
    username = params.get("username")
    if username is None:
        return {
            "message": "Params must have username field",
            "status_code": 400
        }
    database = params.get("database")
    if database is None:
        return {
            "message": "Params must have database field",
            "status_code": 400
        }
    collection = params.get("collection")
    roles, error = mongo.client_read(database="account", collection="User", filters={"username": username}, fields=["roles"])
    if error is not None:
        return error
    for role_id in roles[0]["roles"]:
        role, error = mongo.client_read(database="account", collection="Role", filters={"_id": role_id["destination_id"]}, fields=None)
        if error is not None:
             return error
        if role and role[0]["database"] == database:
            if collection:
                if collection in role[0]["collection"]:
                    return None
                else:
                    return {
                        "message": f"User {username} don't have permission to access {database}.{collection}",
                        "status_code": 400
                    }
            return None
    else:
        return {
                "message": f"User {username} don't have permission to access {database}",
                "status_code": 400
            }

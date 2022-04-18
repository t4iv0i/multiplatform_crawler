from threading import Thread
from module import facebook, mongo, helper
from models.cache import Cache


def upsert_cache(data, params):
    path = params["path"]
    if path == "":
        origin = dict(uuid=params["uuid"], username=params["username"], params=params, data=data)
    else:
        filters = {}
        for key in Cache.index:
            filters[key] = params[key]
        origin, error = mongo.client_read(database="cache", collection="Cache", filters=filters, fields=None)
        if error is not None:
            return error
        if len(origin):
            origin = origin[0]
            origin["data"] = helper.recursive_insert(origin=origin["data"], data=data, path=path)
    result = mongo.client_upsert(database="cache", collection="Cache", data=origin)
    return result


class Daemon(Thread):
    def __init__(self, rabbitmq_pool):
        super().__init__()
        self.function = {
            'facebook': facebook.get_node_info,
            # 'instagram': get_service.get_instagram_info,
            # 'tiktok':  get_service.get_tiktok_info,
            # 'youtube': get_service.get_youtube_info
        }
        self.rabbitmq_pool = rabbitmq_pool

    def run(self):
        print("Started Daemon...")
        consumer = self.rabbitmq_pool.consumer(queue_name="daemon")
        _ = next(consumer)
        while True:
            message, error = next(consumer)
            if error is not None:
                continue
            else:
                data, params = message
                print(params)
                username = params["username"]
                uuid = params["uuid"]
                database = params["database"]
                collection = params["collection"]
                path = params["path"]
                result = mongo.client_upsert(database=database, collection=collection, data=data)
                print(result[0])
                result = upsert_cache(data=data, params=params)
                print(result[0])
                for connection_params in params.get("connections", []):
                    connection_params.update({"username": username, "uuid": uuid, "database": database})
                    connection_name = connection_params["connection_name"]
                    connection_path = path + "{" + connection_name + "}"
                    connection_data = data[connection_name]
                    for data_index in range(len(connection_data)):
                        record = connection_data[data_index]
                        data_path = connection_path + f"[{data_index}]"
                        connection_params.update({"collection": record["collection"], "path": data_path})
                        node_data, error = facebook.get_info(uid=record["id"], requirement=connection_params)
                        if error is not None:
                            print(str(error))
                            continue
                        self.rabbitmq_pool.publish(queue_name="daemon", message=(node_data, connection_params))

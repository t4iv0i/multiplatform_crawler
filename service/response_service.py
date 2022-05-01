from service import mongo_service
from module import mongo


def get_info(params):
    data, error = mongo_service.read_data(params)
    if error is not None:
        return None, error
    database, collection = params["database"], params["collection"]
    if database == "cache" and collection == "Cache":
        for index in range(len(data)):
            filters = {"_id": data[index]["_id"]}
            mongo.client_delete(database=database, collection=collection, filters=filters, count=params["limit"])
            data[index] = data[index]["data"]
    return data, None

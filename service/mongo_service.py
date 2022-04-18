from module import mongo


def read_data(params):
    database = params["database"]
    collection = params["collection"]
    filters = params.get("filters")
    fields = params.get("fields")
    limit = params.get("limit")
    connections = params.get("connections", [])
    data, error = mongo.client_read(database=database, collection=collection, filters=filters, fields=fields, limit=limit)
    if error is not None:
        return None, error
    for connection_params in connections:
        connection_name, connection_filters = connection_params["connection_name"], connection_params.get("filters", {})
        for data_index in range(len(data)):
            record = data[data_index]
            connection_index, connection_data = dict(), list()
            for link in record.get(connection_name, []):
                connection_database = link["database"]
                connection_collection = link["collection"]
                connection_id = link["id"]
                if connection_index.get((connection_database, connection_collection)):
                    connection_index[(connection_database, connection_collection)].append(connection_id)
                else:
                    connection_index[(connection_database, connection_collection)] = [connection_id]
            for (_database, _collection), _index in connection_index.items():
                connection_params["database"] = _database
                connection_params["collection"] = _collection
                connection_filters["id"] = {"$in": _index}
                connection_params["filters"] = connection_filters
                _data, error = read_data(params=connection_params)
                if error is not None:
                    return None, error
                connection_data += _data
            if record.get(connection_name):
                record[connection_name].append(connection_data)
            else:
                record[connection_name] = connection_data
            data[data_index] = record
    return data, None


# def upsert_data(params, data):
#     database = params["database"]
#     collection = params["collection"]
#     model = Model.get(database=database, collection=collection)
#     index_filter = dict()
#     if type(data) == dict:
#         data = [data]
#     result = mongo.client_upsert(database=database, collection=collection, data=data)
#     success = list(map(lambda index: (result[index], data[index]), range(len(data))))
#     for connection_params in params.get("connection", []):
#         connection_name = connection_params["connection_name"]
#         for index, record in success:
#             if record.get(connection_name):
#                 connection_data = record[connection_name]
#                 source_link_data = {"collection": collection, "id": record["id"]}
#                 connection_object_id, error = upsert_data(params=connection_params, data=connection_data)
#                 exist_connection_index = list()
#                 if error is not None:
#                     return None, error
#                 for field in model.index:
#                     index_filter[field] = record[field]
#                 document, error = mongo.client_read(database=database, collection=collection, filters=index_filter, fields=None)
#                 if error is not None:
#                     return None, error
#                 for _data in document[0].get(connection_name, []):
#                     if _data.get('id'):
#                         exist_connection_index.append(_data['id'])
#                 check_exist = dict([(index, True) for index in exist_connection_index])
#                 for _data in connection_data[::-1]:
#                     _index = _data["id"]
#                     dest_link_data = {"collection": connection_params["collection"], "id": _index}
#                     reference_data = {"source": source_link_data, "destination": dest_link_data}
#                     result = mongo.client_upsert(database=database, collection="Reference", data=reference_data)
#                     if not check_exist[_index]:
#                         exist_connection_index.append(_index)
#                 record[connection_name] = exist_connection_index
#                 result = mongo.client_upsert(database=database, collection=collection, data=record)
#     return [index for index, _ in success], None

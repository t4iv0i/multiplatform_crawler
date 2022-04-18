from app import database_pool
from models import Model
from datetime import datetime, timezone


def client_read(database, collection, filters, fields, limit=0):
    db_client = database_pool.get_client(database=database)
    db_session = database_pool.get_inactive_session(database=database)
    collection = db_client.database[collection]
    try:
        documents = collection.find(filter=filters, projection=fields, limit=limit, session=db_session.session)
    except Exception as e:
        return None, {
            "message": f"Cant read data. Detail: {str(e)}",
            "status_code": 400
        }
    result = list(map(lambda document: document, documents))
    documents.close()
    database_pool.set_active_session(db_session)
    return result, None


def client_upsert(database, collection, data):
    db_client = database_pool.get_client(database=database)
    db_session = database_pool.get_inactive_session(database=database)
    model = Model.get(database=database, collection=collection)
    collection = db_client.database[collection]
    result, index_filters = list(), dict()
    if type(data) == dict:
        data = [data]
    for raw in data:
        for field in model.index:
            index_filters[field] = raw[field]
        document = collection.find(filter=index_filters, session=db_session.session)
        document = list(map(lambda d: d, document))
        value = model(raw)
        record = value.to_record()
        now = datetime.now(tz=timezone.utc)
        record["system_updated_time"] = now
        if document and document[0].get("system_created_time"):
            record["system_created_time"] = document[0]["system_created_time"]
        else:
            record["system_created_time"] = now
        update = {'$set': record}
        update_result = collection.find_one_and_update(filter=index_filters, update=update, projection="_id", session=db_session.session)
        if update_result is None:
            update_result = collection.update_one(filter=index_filters, upsert=True, update=update, session=db_session.session)
            result.append(update_result.upserted_id)
        else:
            result.append(update_result["_id"])
    database_pool.set_active_session(db_session)
    return result


def client_delete(database, collection, filters, count):
    db_client = database_pool.get_client(database=database)
    db_session = database_pool.get_inactive_session(database=database)
    collection = db_client.database[collection]
    documents = list()
    for i in range(count):
        document = collection.find_one_and_delete(filter=filters, session=db_session.session)
        if document:
            documents.append(document)
        else:
            break
    database_pool.set_active_session(db_session)
    return documents

from importlib import import_module
import re


class Model:
    models = dict()
    for db_name in ["template", "account", "cache", "facebook", "instagram", "tiktok", "youtube", "reference"]:
        models[db_name] = dict()
        database = import_module(f'models.{db_name}')
        attributes = dir(database)
        collection_names = list(filter(lambda n: re.findall(r'^[A-Z]\w+', n), attributes))
        for collection_name in collection_names:
            model = getattr(database, collection_name)
            models[db_name][collection_name] = model
            test = model({})

    @classmethod
    def get(cls, database, collection):
        if cls.models.get(database) and cls.models[database].get(collection):
            return cls.models[database][collection]
        else:
            return None

    @classmethod
    def get_database_names(cls):
        return list(cls.models.keys())

    @classmethod
    def get_model_names(cls, database):
        if cls.models.get(database):
            return list(cls.models[database].keys())
        else:
            return None

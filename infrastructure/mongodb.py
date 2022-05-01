import config
from pymongo import MongoClient, errors


class Client:
    def __init__(self, database):
        self.database = database
        self.client = MongoClient(host=config.MONGO_HOST,
                                  port=config.MONGO_PORT,
                                  username=config.MONGO_USERNAME,
                                  password=config.MONGO_PASSWORD,
                                  serverSelectionTimeoutMS=config.MONGO_CONNECTION_TIMEOUT_MS)
        try:
            self.client.server_info()
        except errors.NetworkTimeout as ex:
            raise ex
        else:
            print(f"Initialized {database} mongo client")
        self.database = self.client[database]

    def generate_session(self):
        return self.client.start_session(causal_consistency=True)

    def switch_collection(self, collection):
        self.database = self.client[self.database][collection]

    def reconnect(self):
        del self.client
        self.client = MongoClient(host=config.MONGO_HOST,
                                  port=config.MONGO_PORT,
                                  username=config.MONGO_USERNAME,
                                  password=config.MONGO_PASSWORD,
                                  serverSelectionTimeoutMS=config.MONGO_CONNECTION_TIMEOUT_MS)


class Session:
    def __init__(self, name, database, session):
        print(f"Initialized {name}")
        self.name = name
        self.database = database
        self.session = session


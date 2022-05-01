from service import get_service, mongo_service
from module import mongo
from threading import Thread, Event


class Worker(Thread):
    def __init__(self, name, rabbitmq_pool):
        super().__init__()
        self.stop_event = Event()
        self.name = name
        self.rabbitmq_pool = rabbitmq_pool
        self.function = dict()
        self.function['facebook'] = get_service.get_facebook_info
        self.function['instagram'] = get_service.get_instagram_info
        self.function['tiktok'] = get_service.get_tiktok_info
        self.function['youtube'] = get_service.get_youtube_info

    def stop(self):
        self.stop_event.set()

    def run(self):
        print(f"{self.name} is started...")
        consumer = self.rabbitmq_pool.consumer(queue_name="worker")
        connection_name = next(consumer)
        while True:
            if self.stop_event.is_set():
                self.rabbitmq_pool.set_connection_signal(connection_name=connection_name, signal="kill_consumer")
                print(f"{self.name} is stopped!!!")
                break
            params, error = next(consumer)
            if error is not None:
                continue
            else:
                typ3 = params["database"]
                node_data, error = self.function[typ3](params)
                if error is not None:
                    print(error)
                    params['retry'] -= 1
                    if params['retry'] > 0:
                        self.rabbitmq_pool.publish(queue_name='worker', message=params)
                    continue
                print(node_data)
                database, collection = params["database"], params["collection"]
                result = mongo.client_upsert(database=database, collection=collection, data=node_data)
                print(result)
                uuid, username = params.pop("uuid"), params.pop("username")
                data = {"uuid": uuid, "username": username, "params": params, "data": node_data}
                result = mongo.client_upsert(database="cache", collection="Cache", data=data)
                print(result)



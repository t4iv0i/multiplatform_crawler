from time import sleep
from service import get_service, mongo_service
from module import mongo
from random import uniform
from threading import Thread, Event


class Worker(Thread):
    def __init__(self, name, typ3, rabbitmq_pool):
        super().__init__()
        self.stop_event = Event()
        self.name = name
        self.type = typ3
        self.rabbitmq_pool = rabbitmq_pool
        if typ3 == 'facebook':
            self.function = get_service.get_facebook_info
        # elif typ3 == 'instagram':
        #     self.function = post_params_service.get_instagram_info
        # elif typ3 == 'tiktok':
        #     self.function = post_params_service.get_tiktok_info
        # elif typ3 == 'youtube':
        #     self.function = post_params_service.get_youtube_info

    def stop(self):
        self.stop_event.set()

    def run(self):
        print(f"{self.name} is started...")
        consumer = self.rabbitmq_pool.consumer(queue_name=self.type)
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
                params["type"] = self.type
                generator = self.function(params)
                node_data, error = next(generator)
                if error is not None:
                    print(error)
                    params['retry'] -= 1
                    if params['retry'] > 0:
                        self.rabbitmq_pool.publish(queue_name=self.type, message=params)
                    continue
                params.pop("connections")
                params["path"] = ""
                self.rabbitmq_pool.publish(queue_name="daemon", message=(node_data, params))
                for connection_data, connection_params in generator:
                    print(connection_data)
                    self.rabbitmq_pool.publish(queue_name="daemon", message=(connection_data, connection_params))

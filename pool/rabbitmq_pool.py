import pika
import json
import config
from module import helper
from threading import Lock
from time import sleep


class RabbitMQPool:
    def __init__(self):
        credentials = pika.PlainCredentials(username=config.RABBITMQ_USERNAME, password=config.RABBITMQ_PASSWORD)
        self.parameters = pika.ConnectionParameters(host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT, credentials=credentials)
        self.connections = dict()
        self.connection_signals = dict()
        self.inactive_connections = list()
        self.lock = Lock()
        connection_name = self.init_connection()
        connection = self.connections[connection_name]
        channel = connection.channel()
        for queue_name in config.QUEUE_NAMES:
            channel.queue_declare(queue=queue_name, auto_delete=False)

    def init_connection(self):
        self.lock.acquire()
        exist_connection_names = list(self.connections.keys())
        connection_name = helper.generate_name("rabbitmq", exist_connection_names)
        connection = pika.BlockingConnection(self.parameters)
        self.connections[connection_name] = connection
        self.inactive_connections.append(connection_name)
        self.lock.release()
        print(f"RabbitMQ init connection {connection_name}")
        return connection_name

    def set_connection_signal(self, connection_name, signal):
        self.lock.acquire()
        self.connection_signals[connection_name] = signal
        self.lock.release()

    def get_connection_signal(self, connection_name):
        self.lock.acquire()
        signal = self.connection_signals.get(connection_name)
        self.lock.release()
        return signal

    def get_active_connection(self):
        self.lock.acquire()
        if len(self.inactive_connections) == 0:
            self.lock.release()
            return None, None
        connection_name = self.inactive_connections.pop(0)
        self.lock.release()
        return connection_name, self.connections[connection_name]

    def set_active_connection(self, connection_name):
        self.lock.acquire()
        self.inactive_connections.append(connection_name)
        self.lock.release()

    def reset_connection(self, connection_name):
        self.lock.acquire()
        self.connections[connection_name].close()
        self.connections[connection_name] = pika.BlockingConnection(self.parameters)
        if connection_name not in self.inactive_connections:
            self.inactive_connections.append(connection_name)
        self.lock.release()
        print(f"RabbitMQ reset connection {connection_name}")

    def consumer(self, queue_name):
        connection_name, connection = self.get_active_connection()
        while connection is None:
            self.init_connection()
            connection_name, connection = self.get_active_connection()
        yield connection_name
        channel = connection.channel()
        consume = channel.consume(queue=queue_name, auto_ack=True)
        while True:
            signal = self.get_connection_signal(connection_name)
            if signal == "kill_consumer":
                channel.cancel()
                self.set_active_connection(connection_name)
                break
            method_frame, header_frame, body = next(consume)
            try:
                message = json.loads(body.decode('utf-8'))
            except Exception as e:
                channel.cancel()
                self.reset_connection(connection_name)
                connection_name, connection = self.get_active_connection()
                channel = connection.channel()
                consume = channel.consume(queue=queue_name, auto_ack=True)
                yield None, f"Error occurs when get message from queue: {str(e)}"
            else:
                yield message, None

    def publish(self, message, queue_name):
        connection_name, connection = self.get_active_connection()
        while connection is None:
            self.init_connection()
            connection_name, connection = self.get_active_connection()
        error = None
        for count in range(3):
            with connection.channel() as channel:
                try:
                    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
                except Exception as e:
                    self.reset_connection(connection_name)
                    error = f"Error occurs when publish message: {str(e)}"
                    print(error)
                    sleep(1.5)
                else:
                    self.set_active_connection(connection_name)
                    return None
        return error


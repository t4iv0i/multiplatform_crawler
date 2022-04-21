API_PREFIX = '/api/v2_3'

# -------------------------------------
# MongoDB
# -------------------------------------
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = 'thangnm'
MONGO_PASSWORD = '0139'
MONGO_CONNECTION_TIMEOUT_MS = 10000
MONGO_DATABASE = 'mutiplatform-crawler'

# -------------------------------------
# Rabbit MQ
# -------------------------------------
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'testiny'
RABBITMQ_PASSWORD = '0139'
RABBITMQ_MAX_CHANNEL = 16
EXCHANGE_NAME = ''
QUEUE_NAMES = ['worker']

# -------------------------------------
# JWT
# -------------------------------------
ACCESS_TOKEN_EXPRISE = 60
JWT_SECRET_KEY = "accesstrade"

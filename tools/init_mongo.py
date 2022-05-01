import config
from pymongo import MongoClient
from datetime import datetime
from models import Model
from hashlib import md5


client = MongoClient(host=config.MONGO_HOST,
                     port=config.MONGO_PORT,
                     username=config.MONGO_USERNAME,
                     password=config.MONGO_PASSWORD)

database = client["account"]
droper = database["Role"]
droper.drop()
role = database["Role"]
roles = list()
for db_name in ["facebook", "instagram", "tiktok", "youtube", "cache"]:
    document = {"database": db_name, "collection": Model.get_model_names(db_name),
                "system_created_time": datetime.utcnow(), "system_updated_time": datetime.utcnow()}
    index = role.insert_one(document=document)
    roles.append({"destination": "Role", "destination_id": index.inserted_id})

droper = database["User"]
droper.drop()
user = database["User"]
username = "koc"
password = "kocvietnam2023"
hash_password = md5(password.encode("utf-8")).hexdigest()
document = {"username": username, "hash_password": hash_password, "status": "active", "roles": roles,
            "created_time": datetime.utcnow(), "updated_time": datetime.utcnow()}
user_index = user.insert_one(document=document)

droper = database["Reference"]
droper.drop()
reference = database["Reference"]
for document in roles:
    document.update({"source": "User", "source_id": user_index.inserted_id, "created_time": datetime.utcnow(), "updated_time": datetime.utcnow()})
    reference.insert_one(document=document)



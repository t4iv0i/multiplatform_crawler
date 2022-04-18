from module import mongo
import hashlib


def login(username, password):
    filters = dict(username=username)
    user, error = mongo.client_read(database="account", collection="User", filters=filters, fields=["hash_password"])
    if error is not None:
        return False, dict(message=f"Can't read account.User", status_code=400)
    if user is None or len(user) == 0:
        return False, dict(message=f"Username {username} not exist.", status_code=400)
    hash_password = hashlib.md5(password.encode("utf-8")).hexdigest()
    if hash_password != user[0]["hash_password"]:
        return False, dict(message="Wrong password.", status_code=400)
    else:
        return True, dict(message="Login successfully", status_code=200)

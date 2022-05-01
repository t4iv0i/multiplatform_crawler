import config
import json
from flask import Blueprint, request, make_response, jsonify
from flask_cors import CORS
from module import validation
from service import user_service
import datetime
from flask_jwt_extended import create_access_token


bp_login = Blueprint(name='bp_login', import_name=__name__)
CORS(bp_login)


# -----------------------------------------
# Login
# -----------------------------------------
@bp_login.route('/login', methods=['POST'])
def login():
    try:
        data = json.loads(request.data)
    except:
        return make_response(jsonify(message="Data must be JSON type"), 400)

    status, message = validation.validate_login(data)
    if not status:
        return make_response(jsonify(message))

    username, password = data['username'], data['password']
    status, message = user_service.login(username=username, password=password)
    if status:
        exprise_delta = datetime.timedelta(minutes=config.ACCESS_TOKEN_EXPRISE)
        access_token = create_access_token(identity=username, expires_delta=exprise_delta)
        return make_response(jsonify(access_token=access_token), 200)
    else:
        return make_response(jsonify(message), 200)

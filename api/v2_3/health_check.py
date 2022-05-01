import json
from flask import Blueprint, request, make_response, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import errors

bp_health_check = Blueprint(name='bp_health_check', import_name=__name__)
CORS(bp_health_check)


@bp_health_check.route('/file', methods=['GET'])
@jwt_required
def health_check():
    mongodb_connection = True

    try:
        mongo.client.server_info()
    except errors.NetworkTimeout:
        mongodb_connection = False

    message = {
        "MongoDB": mongodb_connection
    }

    return make_response(jsonify(message=message), 200)
import json
from flask import Blueprint, request, make_response, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from module import validation
from uuid import uuid4
from app import rabbitmq_pool


bp_post_params = Blueprint(name='bp_post_params', import_name=__name__)
CORS(bp_post_params)


@bp_post_params.route('/post_params', methods=['POST'])
@jwt_required()
def post_params():
    try:
        data = json.loads(request.data)
    except json.decoder.JSONDecodeError:
        return make_response(jsonify(error='Data must be JSON type'), 400)
    if type(data) == dict:
        data = [data]
    result = list()
    for params in data:
        normalized_params, error = validation.validate_post_params(params=params)
        if error is not None:
            return make_response(jsonify(error=error["message"]), error["status_code"])
        username = get_jwt_identity()
        uuid = str(uuid4())
        normalized_params.update(uuid=uuid, username=username, retry=3)
        error = validation.validate_permission(params=normalized_params)
        if error is not None:
            return make_response(jsonify(result=result, error=error["message"]), error["status_code"])
        rabbitmq_pool.publish(queue_name=normalized_params["database"], message=normalized_params)
        result.append(uuid)
    return make_response(jsonify(dict(result=result)), 200)
import json
from flask import Blueprint, request, make_response, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from module import validation, helper
from service import response_service


bp_get_info = Blueprint(name='bp_get_info', import_name=__name__)
CORS(bp_get_info)


@bp_get_info.route('/get_info', methods=['POST'])
@jwt_required()
def get_info():
    try:
        params = json.loads(request.data)
    except json.decoder.JSONDecodeError:
        return make_response(jsonify(error='Data must be JSON type'), 400)
    normalized_params, error = validation.validate_get_info(params=params)
    if error is not None:
        return make_response(jsonify(error=error['message']), error['status_code'])
    username = get_jwt_identity()
    normalized_params.update(username=username)
    error = validation.validate_permission(normalized_params)
    if error is not None:
        return make_response(jsonify(error=error['message']), error['status_code'])
    result, error = response_service.get_info(params=normalized_params)
    if error is not None:
        return make_response(jsonify(error=error), 400)
    else:
        return make_response(jsonify(result=helper.convert(result)), 200)
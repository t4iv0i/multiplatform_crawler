from service import mongo_service


def get_info(params):
    data, error = mongo_service.read_data(params)
    if error is not None:
        return None, error
    return data, None

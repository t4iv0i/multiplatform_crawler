import argparse
import config
from flask import Flask
from flask_jwt_extended import JWTManager
from api.v2_3.health_check import bp_health_check
from api.v2_3.login import bp_login
from api.v2_3.get_info import bp_get_info
from api.v2_3.post_params import bp_post_params


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
jwt = JWTManager(app)


# app.register_blueprint(blueprint=bp_health_check, url_prefix=config.API_PREFIX + '/health_check')

app.register_blueprint(blueprint=bp_login, url_prefix=config.API_PREFIX)

app.register_blueprint(blueprint=bp_get_info, url_prefix=config.API_PREFIX)

app.register_blueprint(blueprint=bp_post_params, url_prefix=config.API_PREFIX)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start')

    parser.add_argument('--host', required=False, type=str, help='Define host (default: %(default)s)')
    parser.add_argument('--port', required=False, type=int, help='Define port (default: %(default)s)')
    parser.add_argument('--debug', required=False, type=bool, help='Define debug mode (default: %(default)s)')

    args = parser.parse_args()

    # Start server
    app.run(host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=False, processes=1)

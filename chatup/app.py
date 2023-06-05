import logging
import os

from flask import Blueprint, Flask
from flask_restx import Api
from flask_cors import CORS

from chatup.api.shops import ns as shops_ns
from chatup.api.health import ns as health_ns
from chatup.config import load

config = load(os.environ.get('ENVIRONMENT', 'local'))
logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    CORS(app, resource={r"/*": {"origins": "*"}})
    v1_blueprint = Blueprint("chatup-db-api", __name__, url_prefix="/v1")
    api_v1 = Api(v1_blueprint, title="ChatUp DB API", version="1.0", description="ChatUp DB API")
    health_blueprint = Blueprint("chatup-db-health", __name__)
    api_health = Api(
        health_blueprint,
        title="chatup db api health",
        description="non-versioned namespaces. SEE /v1 FOR " "THE VERSIONED API",
    )

    api_health.add_namespace(health_ns, path='/health')
    api_v1.add_namespace(shops_ns)
    app.register_blueprint(v1_blueprint)
    app.register_blueprint(health_blueprint)

    return app


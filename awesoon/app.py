import logging
import os

from flask import Blueprint, Flask
from flask_cors import CORS
from flask_restx import Api

from awesoon.api.conversations import api as conversations_ns
from awesoon.api.docs import api as docs_ns
from awesoon.api.health import api as health_ns
from awesoon.api.scans import api as scans_ns
from awesoon.api.shopify import api as shopify_apps_ns
from awesoon.api.shopify_installations import api as shopify_installations_ns
from awesoon.api.shops import api as shops_ns
from awesoon.config import load

config = load(os.environ.get('ENVIRONMENT', 'local'))
logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    CORS(app, resource={r"/*": {"origins": "*"}})
    v1_blueprint = Blueprint("db-api", __name__, url_prefix="/v1")
    api_v1 = Api(v1_blueprint, title="Awesoon DB API", version="1.0", description="Awesoon DB API")
    health_blueprint = Blueprint("awesoon-db-health", __name__)
    api_health = Api(
        health_blueprint,
        title="Awesoon db api health",
        description="non-versioned namespaces. SEE /v1 FOR " "THE VERSIONED API",
    )

    api_health.add_namespace(health_ns, path='/health')
    api_v1.add_namespace(shops_ns)
    api_v1.add_namespace(scans_ns)
    api_v1.add_namespace(shopify_apps_ns)
    api_v1.add_namespace(docs_ns)
    api_v1.add_namespace(shopify_installations_ns)
    api_v1.add_namespace(shopify_installations_ns)
    api_v1.add_namespace(conversations_ns)
    app.register_blueprint(v1_blueprint)
    app.register_blueprint(health_blueprint)

    return app


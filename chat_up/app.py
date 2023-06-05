import logging
import os

from flask import Flask
from flask_restx import Api

from chat_up.api.endpoints import ns as endpoints_ns
from chat_up.api.health import ns as health_ns
from chat_up.config import load

config = load(os.environ.get('ENVIRONMENT', 'local'))
logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    api = Api(title='ChatUp API', version='1.0',
              description='Cookie Cutter API')
    api.add_namespace(health_ns, path='/health')
    api.add_namespace(endpoints_ns, path='/v1')
    api.init_app(app)
    return app


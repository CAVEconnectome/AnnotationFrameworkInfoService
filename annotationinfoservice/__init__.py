from flask import Flask, jsonify, url_for, redirect, Blueprint
from annotationinfoservice.config import configure_app
from annotationinfoservice.database import Base
from annotationinfoservice.utils import get_instance_folder_path
from annotationinfoservice.datasets.api import api_bp
from annotationinfoservice.datasets.views import views_bp
from annotationinfoservice.admin import setup_admin  # noQA: E402
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
import logging
from flask_migrate import Migrate

from werkzeug.middleware.proxy_fix import ProxyFix
from middle_auth_client import auth_required

__version__ = "3.7.0"

db = SQLAlchemy(model_class=Base)
migrate = Migrate()


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def create_app(test_config=None):
    # Define the Flask Object
    app = Flask(
        __name__,
        instance_path=get_instance_folder_path(),
        instance_relative_config=True,
        static_url_path="/info/static",
        static_folder="../static",
    )
    # app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_port=1, x_for=1, x_host=1, x_prefix=1)
    # app.wsgi_app = ReverseProxied(app.wsgi_app)
    logging.basicConfig(level=logging.DEBUG)

    # load configuration (from test_config if passed)
    if test_config is None:
        app = configure_app(app)
    else:
        app.config.update(test_config)

    apibp = Blueprint("api", __name__, url_prefix="/info/api")

    @auth_required
    @apibp.route("/versions")
    def versions():
        return jsonify([2]), 200

    with app.app_context():
        app.register_blueprint(views_bp, url_prefix="/info")
        api = Api(
            apibp, title="Annotation Infoservice API", version=__version__, doc="/doc"
        )
        api.add_namespace(api_bp, path="/v2")

        app.register_blueprint(apibp)
        db.init_app(app)
        migrate.init_app(app, db)
        # db.create_all()
        admin = setup_admin(app, db)

    @app.route("/info/health")
    def health():
        return jsonify("healthy"), 200

    @auth_required
    @app.route("/info/site-map")
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append((url, rule.endpoint))
        # links is now a list of url, endpoint tuples
        return jsonify(links)

    return app

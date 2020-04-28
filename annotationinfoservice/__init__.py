from flask import Flask, jsonify, url_for
from annotationinfoservice.config import configure_app
from annotationinfoservice.database import Base
from annotationinfoservice.utils import get_instance_folder_path
from annotationinfoservice.datasets.api import api_bp
from annotationinfoservice.datasets.views import views_bp
from annotationinfoservice.admin import setup_admin  # noQA: E402
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

__version__ = '0.4.0'

db = SQLAlchemy(model_class=Base)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def create_app(test_config=None):
    # Define the Flask Object
    app = Flask(__name__,
                instance_path=get_instance_folder_path(),
                instance_relative_config=True,
                static_folder="../static")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_port=1, x_for=1, x_host=1, x_prefix=1)
         
    logging.basicConfig(level=logging.DEBUG)

    with app.app_context():
        api = Api(app, title="Annotation Infoservice API", version=__version__, doc="/info/doc")
        api.add_namespace(api_bp, path='/info/api/v2')

    # load configuration (from test_config if passed)
    if test_config is None:
        app = configure_app(app)
    else:
        app.config.update(test_config)
    
    with app.app_context():
        app.register_blueprint(views_bp, url_prefix='/info')
        db.init_app(app)
        db.create_all()
        admin = setup_admin(app, db)
    
    @app.route("/info/health")
    def health():
        return jsonify("healthy"), 200
   
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


    return app

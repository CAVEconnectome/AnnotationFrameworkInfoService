from flask import Flask
# from flask_migrate import Migrate
from .config import configure_app
from .database import Base
from .utils import get_instance_folder_path
from .datasets.controllers import mod_datasets as dataset_bp
from .admin import setup_admin  # noQA: E402
from flask_sqlalchemy import SQLAlchemy

__version__ = '0.0.1'


def create_app(test_config=None):
    # Define the Flask Object
    app = Flask(__name__,
                instance_path=get_instance_folder_path(),
                instance_relative_config=True,
                static_folder="../static")
    # load configuration (from test_config if passed)
    if test_config is None:
        app = configure_app(app)
    else:
        app.config.update(test_config)
    # register blueprints
    app.register_blueprint(dataset_bp, url_prefix='/info')
    with app.app_context():
        db = SQLAlchemy(model_class=Base)
        db.init_app(app)
        db.create_all()
        admin = setup_admin(app, db)

    return app

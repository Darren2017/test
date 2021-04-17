from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from pymongo import MongoClient


db = SQLAlchemy()
client = MongoClient('localhost', 27017)
db_m = client.project
collection_m = db_m.user_movie
collection_l = db_m.like

def create_app(config_name=None, main=True):
    if config_name is None:
        config_name = 'production'
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    with app.app_context():
        db.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app(config_name = 'default')


from .api import api
app.register_blueprint(api, url_prefix='/api/v1.0')
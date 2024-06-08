from flask import Flask
from app.DbManager import DbManager
from app.routes import init_routes
# from models.legacy.old_image_processor import images_processor


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    app.secret_key = app.config['SECRET_KEY']
    init_routes(app)
    return app


app = create_app()

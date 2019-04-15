import logging
from flask import Flask
from flask.logging import default_handler

import multilog
from config import AppConfig
from flask_socketio import SocketIO
from celery import Celery

socketio = SocketIO()
celery = Celery(__name__, broker=AppConfig.CELERY_BROKER_URL)

def create_app():

    app = Flask(__name__)
    app.config.from_object(AppConfig)

    # 配置写入日志文件的handler
    app.logger.removeHandler(default_handler)
    handler = multilog.MyLoggerHandler('flask', encoding='UTF-8', when='H')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    app.logger.addHandler(ch)
    app.logger.setLevel(logging.INFO)

    socketio.init_app(app)
    celery.conf.update(app.config)

    from .blueprint import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v0')

    return socketio, app

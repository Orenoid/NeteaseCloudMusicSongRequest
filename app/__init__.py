import logging
from flask import Flask
from flask.logging import default_handler

import multilog
from .blueprint import api_bp
from config import AppConfig


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

    app.register_blueprint(api_bp, url_prefix='/api/v0')

    return app

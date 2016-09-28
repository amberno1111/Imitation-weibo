# -*- coding: utf-8 -*-
from flask import Flask
from config import config
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
# 创建扩展，暂时不进行初始化，因此不传入程序实例
moment = Moment()
db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请登录后访问'
login_manager.session_protection = 'strong'


def create_app(config_name):
    """
    :summary: 工厂函数，
    :param config_name: 配置名
    :return: app，程序实例
    """
    app = Flask(__name__)
    # 使用Flask中app.config配置对象提供的from_object()方法可以从配置文件config.py中导入配置类
    app.config.from_object(config[config_name])
    # 配置初始化
    config[config_name].init_app(app)
    # 初始化扩展
    moment.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
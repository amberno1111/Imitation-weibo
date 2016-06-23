# -*- coding: utf-8 -*-
from config import config
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown

# 创建扩展类
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
mail = Mail()
pagedown = PageDown()


# 工厂函数
def create_app(config_name):
    # 创建程序
    app = Flask(__name__)
    # 导入配置
    app.config.from_object(config[config_name])
    # 初始化配置
    config[config_name].init_app(app)
    # 初始化扩展
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # 注册auth蓝本，加上一个前缀
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

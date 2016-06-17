# -*- coding: utf-8 -*-
from config import config
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# 创建扩展类
bootstrap = Bootstrap()
moment = Moment()


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
    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

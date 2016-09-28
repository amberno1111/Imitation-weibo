# -*- coding: utf-8 -*-
from . import main
from flask import render_template


# 路由装饰器由蓝本提供，但如果使用 errorhandler 修饰器，
# 那么只有蓝本中的错误才能触发处理程序。要想注册程序全局的错误处理程序，必须使用 app_errorhandler
@main.app_errorhandler(404)
def page_not_found(e):
    """
    :summary: 404错误处理程序
    :param e:
    :return:
    """
    return render_template('main/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    """
    :summary: 500错误处理程序
    :param e:
    :return:
    """
    return render_template('main/500.html'), 500


@main.app_errorhandler(403)
def forbidden(e):
    """
    :summary: 403错误处理程序
    :param e:
    :return:
    """
    return render_template('main/403.html'), 403

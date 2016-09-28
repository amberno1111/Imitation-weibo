# -*- coding: utf-8 -*-
from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)


@main.app_context_processor
def inject_permissions():
    """
    :summary: 把Permission类加入模板上下文，这样就不需要每次都在路由中多传入一个参数了
    :return:
    """
    return dict(Permission=Permission)

# 在最后导入是为了防止循环导入
from . import errors, views

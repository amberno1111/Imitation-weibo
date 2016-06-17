# -*- coding: utf-8 -*-
from . import main
from flask import render_template
from datetime import datetime


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', current_time=datetime.utcnow()), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', current_time=datetime.utcnow()), 500

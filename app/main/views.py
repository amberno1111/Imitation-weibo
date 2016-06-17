# -*- coding: utf-8 -*-
from . import main
from flask import render_template
from datetime import datetime


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

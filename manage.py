# -*- coding: utf-8 -*-
import os
from app import create_app

app = create_app(os.getenv('WEIBO_CONFIG') or 'default')

if __name__ == '__main__':
    app.run()

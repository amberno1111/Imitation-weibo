# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'asdgWS34asRa32Ga3'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
    }
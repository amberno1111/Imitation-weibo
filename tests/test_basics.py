# -*- coding: utf-8 -*-
import unittest
from app import create_app, db
from flask import current_app


# unittest框架要求必须集成unittest.TestCase类
class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        """
        :summary: 必不可少的初始化函数，创建一个测试环境
        :return:
        """
        # 创建app实例
        self.app = create_app('test')
        # app_context()方法创建了一个应用上下文，push方法将这个上下文应用到对应的程序实例上
        self.app_context = self.app.app_context()
        self.app_context.push()
        # 创建数据库表
        db.create_all()

    def tearDown(self):
        """
        :summary: 必不可少的清理程序，删除数据库和程序上下文
        :return:
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 具体的测试用例， 一定要以test开头
    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])




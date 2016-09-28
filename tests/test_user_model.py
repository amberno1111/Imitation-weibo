# -*- coding: utf-8 -*-
import unittest
from app.models import User, Role, Permission, AnonymousUser
from app import create_app, db
import time


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        """
        :summary: 测试密码可以生成password_hash
        :return:
        """
        u = User(password='a')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        """
        :summary: 测试密码可写不可读
        :return:
        """
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        """
        :summary: 测试密码可以验证
        :return:
        """
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        """
        :summary: 测试，即使由同一个密码生成的password_hash也是不一样的
        :return:
        """
        u = User(password='cat')
        u1 = User(password='cat')
        self.assertFalse(u.password_hash == u1.password_hash)

    def test_valid_reset_token(self):
        """
        :summary: 测试，可以生成和验证重设密码
        :return:
        """
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        """
        :summary: 测试，用户的reset token只能自己用
        :return:
        """
        u = User(password='cat')
        u1 = User(password='dog')
        db.session.add(u)
        db.session.add(u1)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(u1.reset_password(token, 'bird'))
        self.assertTrue(u1.verify_password('dog'))

    def test_expired_reset_token(self):
        """
        :summary: 测试，reset token有时效性
        :return:
        """
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token(expiration=1)
        time.sleep(2)
        self.assertFalse(u.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('cat'))

    def test_roles_and_permissions(self):
        """
        :summary: 测试角色和权限
        :return:
        """
        Role.insert_roles()
        u = User(email='a@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.WRITE_ARTICLE))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.ADMINISTER))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        """
        :summary: 测试匿名用户的权限
        :return:
        """
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))



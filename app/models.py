# -*- coding: utf-8 -*-
from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    # 设置password的只写不可读属性
    @property
    def password(self, password):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 检验密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    
# 使用flask-login扩展必须提供的回调函数
# 用于从会话中存储的ID加载用户对象
# 接收一个用户id作为输入，返回相应的用户对象
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
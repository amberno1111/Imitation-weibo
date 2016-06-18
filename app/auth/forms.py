# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import BooleanField, StringField, SubmitField, PasswordField
from wtforms import ValidationError
from wtforms.validators import Email, Length, DataRequired, Regexp, EqualTo
from ..models import User


class LoginForm(Form):
    email = StringField('账户', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我', default=False)
    submit = SubmitField('登陆')


class RegistrationForm(Form):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(
        '昵称',
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                '^[A-Za-z][A-Za-z0-9]*$',
                0,
                '用户名必须是字母、数字')
    ])
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(),
            Length(1, 64),
            EqualTo('password2', message='两次密码不一致')
        ])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    # 验证邮箱和用户名是否已经被使用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')

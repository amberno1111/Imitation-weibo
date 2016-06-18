# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import BooleanField, StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, DataRequired


class LoginForm(Form):
    email = StringField('账户', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我', default=False)
    submit = SubmitField('登陆')

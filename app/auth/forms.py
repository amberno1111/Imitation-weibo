# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from app.models import User
from flask_login import current_user


class LoginForm(Form):
    """
    用户登录表单
    """
    email = StringField(validators=[DataRequired(message='邮箱不能为空'), Email(message='邮箱格式填写错误'), Length(1, 64)])
    password = PasswordField(validators=[DataRequired(message='密码不能为空'), Length(1, 64)])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    """
    用户注册表单
    """
    email = StringField('', validators=[DataRequired(message='邮箱不能为空'), Email(message='邮箱格式填写错误'), Length(1, 64, message='名称太长了')])
    username = StringField(
        '',
        validators=[
            DataRequired(message='用户名不能为空'), Length(1, 64, message='名称太长了'),
            Regexp(
                '^[A-Za-z][A-Za-z0-9]*$',
                0,
                '用户名必须是字母、数字')
        ])
    password = PasswordField('', validators=[DataRequired(message='密码不能为空'), Length(1, 64, message='密码太长了')])
    submit = SubmitField('注册')

    def validate_email(self, field):
        """
        :summary: 检测邮箱是否已经被注册
        :param field:
        :return:
        """
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError('邮箱已经被使用')

    def validate_username(self, field):
        """
        :summary: 检测用户名是否已经被使用
        :param field:
        :return:
        """
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError('用户名已经被使用')


class ChangePasswordForm(Form):
    """
    用户修改密码表单
    """
    current_password = PasswordField(validators=[DataRequired(message='密码不能为空'), Length(1, 64)])
    new_password = PasswordField(
        validators=[
            DataRequired(message='密码不能为空'), Length(1, 64, message='密码太长了'),
            EqualTo('confirm_new_password', message='两次密码不匹配')
        ])
    confirm_new_password = PasswordField(validators=[DataRequired(message='密码不能为空')])
    submit = SubmitField('保存更改')

    def validate_current_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('当前密码输入错误')


class ResetPasswordRequestForm(Form):
    """
    重设密码请求的表单
    """
    email = StringField(
        validators=[
            DataRequired(message='邮箱不能为空'),
            Email(message='邮箱格式填写错误'),
            Length(1, 64, message='邮箱太长了')
        ])
    submit = SubmitField('发送重置密码邮件')

    def validate_email(self, field):
        """
        :summary: 检测邮箱是否已经被注册
        :param field:
        :return:
        """
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError('账户不存在，请核对您输入的邮箱')


class ResetPasswordForm(Form):
    """
    重设密码表单
    """
    email = StringField(
        validators=[
            DataRequired(message='邮箱不能为空'),
            Email(message='邮箱格式填写错误'),
            Length(1, 64, message='邮箱太长了')
        ])
    new_password = PasswordField(
        validators=[
            DataRequired(message='密码不能为空'), Length(1, 64, message='密码太长了'),
            EqualTo('confirm_new_password', message='两次密码不匹配')
        ])
    confirm_new_password = PasswordField(validators=[DataRequired(message='密码不能为空')])
    submit = SubmitField('重设密码')

    def validate_email(self, field):
        """
        :summary: 检测邮箱是否已经被注册
        :param field:
        :return:
        """
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError('账户不存在，请核对您输入的邮箱')


class EditProfileForm(Form):
    """
    用户级别的资料编辑器
    """
    username = StringField('昵称', validators=[DataRequired(message="昵称不能为空"), Length(1, 64, message='名称太长了')])
    real_name = StringField('真实姓名', validators=[Length(0, 64, message='名称太长了')])
    location = StringField('所在城市', validators=[Length(0, 64, message='城市名称太长了')])
    about_me = StringField('个人简介', validators=[Length(0, 512, message='个人简介太长了')])
    submit = SubmitField('保存更改')














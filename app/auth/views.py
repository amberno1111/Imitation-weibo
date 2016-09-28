# -*- coding: utf-8 -*-
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordRequestForm
from .forms import EditProfileForm
from . import auth
from app import db
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, redirect, url_for, flash
from app.models import User
from datetime import datetime
from app.email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('无效的用户名和密码')
    return render_template('auth/login.html', login_form=login_form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(
            email=register_form.email.data,
            username=register_form.username.data,
            password=register_form.password.data
        )
        db.session.add(user)
        db.session.commit()
        send_email(
            recipient=user.email,
            subject='Thank you for register',
            template='auth/email/welcome',
            user=user
        )
        login_user(user, remember=True)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', register_form=register_form)


@auth.route('/logout')
def logout():
    """
    :summary: 用户登出视图
    :return:
    """
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/settings')
@login_required
def settings():
    """
    :summary: 用户设置视图函数
    :return:
    """
    return render_template('auth/settings.html')


@auth.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    :summary: 用户修改密码视图函数
    :return:
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        db.session.commit()
        flash('你已经成功修改密码')
        return redirect(url_for('auth.settings'))
    return render_template('auth/change_password.html', form=form)


# @auth.route('/confirm/<token>')
# @login_user
# def confirm(token):
#     """
#     :summary: 用户确认账户路由
#     :param token:
#     :return:
#     """
#     if current_user.confirmed:
#         return redirect(url_for('main.index'))
#     if current_user.confirm_confirmation_token(token):
#         flash('账户已经验证，谢谢')
#     else:
#         flash('验证账户链接无效或这已过期，请重新获取')
#     return redirect(url_for('main.index'))
#


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    :summary:
    :return:
    """
    form = ResetPasswordRequestForm()
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                recipient=form.email.data,
                subject='重设密码',
                template='auth/email/reset_password',
                token=token, user=current_user
        )
        flash('重设密码的邮件已经发送，请查收')
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    :summary: 重设密码视图函数
    :param token:
    :return:
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.reset_password(token=token, new_password=form.new_password.data):
            flash('重设密码成功，请登录')
            return redirect(url_for('auth.login'))
        else:
            flash('链接已经失效，请重新获取重设密码链接')
            return redirect(url_for('auth.reset_password_request'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/settings/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    :summary: 用户级别的资料编辑器
    :return:
    """
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.real_name = form.real_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        return redirect(url_for('auth.settings'))
    form.username.data = current_user.username
    form.real_name.data = current_user.real_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('auth/edit_profile.html', form=form)



























# -*- coding: utf-8 -*-
from .forms import LoginForm, RegistrationForm
from . import auth
from flask import render_template, redirect, url_for, request
from ..models import User
from flask_login import login_user, flash, login_required, logout_user
from flask_login import current_user
from .. import db
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('欢迎登陆')
            return redirect(url_for('main.index'))
        flash('邮件或密码填写错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Confirm your account',
            'auth/email/confirm',
            token=token,
            user=user
        )
        flash('注册成功，验证邮件已发送至您的邮箱，请验证您的账户')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('宝宝的账户已验证，现在可以访问此网站的任何页面了')
    else:
        flash('验证链接已失效')
    return redirect(url_for('main.index'))


@auth.route('/rensend_confirmation_email')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        'Confirm your account',
        'auth/email/confirm',
        token=token,
        user=current_user
    )
    flash('一封新的验证邮件已发送至您的邮箱，请查收')
    return redirect(url_for('main.index'))
























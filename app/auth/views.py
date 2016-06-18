# -*- coding: utf-8 -*-
from .forms import LoginForm
from . import auth
from flask import render_template, redirect, url_for
from ..models import User
from flask_login import login_user, flash, login_required, logout_user


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

# -*- coding: utf-8 -*-
from . import main
from flask import render_template, abort, flash, redirect, url_for
from datetime import datetime
from ..models import User, Role
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..decorators import admin_required


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@main.route('/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.real_name = form.real_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        flash('你的资料已更新')
        db.session.add(current_user)
        return redirect(url_for('main.user_profile', username=current_user.username))
    form.real_name.data = current_user.real_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.real_name = form.real_name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        flash('资料已更新')
        db.session.add(user)
        return redirect(url_for('main.user_profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.real_name.data = user.real_name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)






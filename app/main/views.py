# -*- coding: utf-8 -*-
from . import main
from flask import render_template, abort, flash, redirect, url_for, request
from flask import current_app
from datetime import datetime
from ..models import User, Role, Permission, Post
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(
            body = form.body.data,
            # current_user通过线程内的代理对象实现，它只是一个轻量的包装
            # 而数据库需要获得真正的用户对象
            author = current_user._get_current_object()
        )
        db.session.add(post)
        return redirect(url_for('main.index'))
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    # 为了显示某页中的记录，需要使用flask-sqlalchemy提供的paginate方法
    # 页数是paginate方法的唯一必须参数提供的 paginate() 方法。
    # 可选参数 per_page 指定每页显示的记录数量；如果没有指定，则默认显示 20 个。
    # 另一个可选参数为 error_out，当其设为 True 时（默认值），如果请求的页数超出了范围，则会返回 404 错误；如果设为 False，页数超出范围时会返回一个空列表。
    # paginate()方法的返回值是一个Pagination类对象，这个类在flask-sqlalchemy中定义，items属性表示当前页面中的记录
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


@main.route('/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


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


@main.route('/post/<int:id>')
def post(id):
    the_post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[the_post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author \
            and not current_user.can(Permission.ADMINISTRATOR):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('你已经关注了此用户')
        return redirect(url_for('main.user_profile', username=user.username))
    current_user.follow(user)
    flash('你成功关注了%s' % user.username)
    return redirect(url_for('main.user_profile', username=user.username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('你没有关注这个用户')
        return redirect(url_for('main.index'))
    current_user.unfollow(user)
    flash('你已经取消关注了%s' % user.username)
    return redirect(url_for('main.index'))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('此用户不存在')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [
        {'user': item.follower, 'timestamp': item.timestamp}
        for item in pagination.items]
    return render_template(
        'followers.html', user=user,
        pagination=pagination, follows=follows,
        title='Followers of', endpoint='main.followers')


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [
        {'user': item.followed, 'timestamp': item.timestamp}
        for item in pagination.items]
    return render_template(
        'followers.html', user=user,
        pagination=pagination, follows=follows,
        title='Followers of', endpoint='main.followed_by')










# -*- coding: utf-8 -*-
from . import main
from app import db
from flask import render_template, redirect
from flask import url_for, flash, abort, request
from flask import current_app, make_response
from app.models import User, Permission, Post, Comment
from .forms import PostForm, CommentForm
from flask_login import current_user, login_required
import os
from config import basedir
from ..decorators import permission_required


# 路由装饰器由蓝本提供
@main.route('/', methods=['GET', 'POST'])
def index():
    """
    :summary: 首页，包含一个发表post的表单
    :return:
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.body.data,
            author=current_user._get_current_object()
        )
        db.session.add(post)
        db.session.commit()
        # 创建一个文件夹来存储文章对应的图片
        os.system('mkdir %s/app/static/img/posts/%s' % (basedir, post.id))
        return redirect(url_for('main.index'))
        # 为了显示某页中的记录， 要把 all() 换成 Flask-SQLAlchemy 提供的 paginate() 方法。
        # 页数是 paginate() 方法的第一个参数，也是唯一必需的参数。可选参数 per_page 用来指定每页显示的记录数量；
        # 如果没有指定，则默认显示 20 个记录。
        # 另一个可选参数为 error_out，当其设为 True 时（默认值），如果请求的页数超出了范围，则会返回 404 错误；
        # 如果设为 False，页数超出范围时会返回一个空列表。
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('main/index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/users/<username>')
def users(username):
    """
    :summary: 用户个人主页视图函数
    :param username:
    :return:
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template(
        'main/users.html', user=user, posts=posts, pagination=pagination)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    """
    :summary: 关注用户视图函数
    :param username:
    :return:
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        return redirect(url_for('main.users', username=username))
    current_user.follow(user)
    flash('成功关注了用户%s' % username)
    return redirect(url_for('main.users', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    :summary: 取消关注视图函数
    :param username:
    :return:
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('您并未关注此用户')
        return redirect(url_for('main.users', username=username))
    current_user.unfollow(user)
    flash('成功取消关注了用户%s' % username)
    return redirect(url_for('main.users', username=username))


@main.route('/followers/<username>')
def followers(username):
    """
    :summary: 粉丝列表页面视图函数
    :param username:
    :return:
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template(
        'main/follows.html', user=user, endpoint='main.followers',
        title="粉丝", pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template(
        'main/follows.html', user=user, title="关注",
        endpoint='.followed', pagination=pagination,
        follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/post/<int:id>', methods=['POST', 'GET'])
def post(id):
    """
    :summary:
    :id:
    :return:
    """
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        return redirect(url_for('main.post', id=post.id))
    comments = post.comments.order_by(Comment.timestamp.desc()).all()
    return render_template('main/post.html', posts=[post], comments=comments, form=form)

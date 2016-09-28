# -*- coding: utf-8 -*-
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from datetime import datetime


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLE = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Follow(db.Model):
    """
    关注关联表
    """
    __tablesname__ = 'follows'
    followed_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True, index=True)
    follower_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model, UserMixin):
    """
    User模型
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    real_name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text(512))
    avatar = db.Column(db.String(128), default='avatar.jpg')
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'Follow', foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship(
        'Follow', foreign_keys=[Follow.followed_id],
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        """
        :summary: User模型初始化函数，生成用户时自动赋予角色，创建用户的数据文件夹，super()函数继承父类，
        :param kwargs:
        """
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    # 设置password的可写不可读
    @property
    def password(self):
        raise AttributeError('密码是一个不可读的属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def verify_password(self, password):
        """
        :summary: 验证密码
        :param password:
        :return:
        """
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        """
        :summary: 生成重设密码的token
        :param expiration:  token失效时间，单位为秒
        :return:
        """
        s = TimedJSONWebSignatureSerializer(
            secret_key=current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset_password': self.id})

    def reset_password(self, token, new_password):
        """
        :summary: 验证token并重设密码
        :param token:
        :param new_password:
        :return:
        """
        s = TimedJSONWebSignatureSerializer(
            secret_key=current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_password') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def can(self, permissions):
        """
        :summary: 检查用户是否具有指定的权限，使用位与操作来实现
        :param permissions:
        :return:
        """
        return self.role is not None and (
            self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """
        :summary: 检查管理员权限的功能经常用到，因此使用单独的方法 is_administrator() 实现
        :return:
        """
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def create_fake(count=100):
        """
        :summary: 创建虚假的用户数据
        :param count: 数量
        :return:
        """
        from random import seed
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        seed()
        for i in range(count):
            u = User(
                email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word(),
                real_name=forgery_py.name.full_name(),
                location=forgery_py.address.city(),
                about_me=forgery_py.lorem_ipsum.sentence(),
                member_since=forgery_py.date.date(True)
            )
            db.session.add(u)
            # 因为用户名和邮箱只能是唯一的，而随机生成的数据可能会重复
            # 因此在数据库提交的时候会引发IntegrityError错误使得程序停止运行
            # 这里使用try来捕获这个异常并且回滚数据库操作，就能保证正常运行
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        """
        :summary: 让用户把自己设置为关注者
        :return:
        """
        for u in User.query.all():
            if not u.is_following(u):
                u.follow(u)
        db.session.add(u)
        db.session.commit()

    def follow(self, user):
        """
        :summary: 关注一个用户
        :param user:
        :return:
        """
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        """
        :summary: 取消关注一个用户
        :param user:
        :return:
        """
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        """
        :summary: 判断是否正在关注某个用户
        :param user:
        :return:
        """
        f = self.followed.filter_by(followed_id=user.id).first()
        return f is not None

    def is_followed_by(self, user):
        """
        :summary: 判断是否被某个用户关注
        :param user:
        :return:
        """
        f = self.followers.filter_by(follower_id=user.id).first()
        return f is not None

    @property
    def followed_posts(self):
        """
        :summary: 获取所关注用户的微博，使用@property装饰器将该方法定义为属性，则在调用时候就可以不用加()
        :return:
        """
        return Post.query.join(
            Follow, Follow.followed_id == Post.author_id).filter(
            Follow.follower_id == self.id)

    # def generate_confirm_token(self, expiration=3600):
    #     """
    #     :summary: 生成账户认证token的函数
    #     :param expiration: token失效时间，单位为秒
    #     :return:
    #     """
    #     s = TimedJSONWebSignatureSerializer(
    #           current_app.config['SECRET_KEY'], expires_in=expiration)
    #     return s.dumps({'confirm': self.id})
    #
    # def confirm_confirmation_token(self, token):
    #     """
    #     :summary: 验证账户认证token
    #     :param token:
    #     :return:
    #     """
    #     s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token)
    #     except:
    #         return False
    #     if data.get('confirm') != self.id:
    #         return False
    #     self.confirmed = True
    #     db.session.add(self)
    #     return True


class AnonymousUser(AnonymousUserMixin):
    """
    出于一致性考虑，还定义了 AnonymousUser 类，并实现了 can() 方法和 is_administrator()方法。
    这个对象继承自 Flask-Login 中的 AnonymousUserMixin 类，并将其设为用户未登录时current_user 的值。
    这样程序不用先检查用户是否登录，就能自由调用 current_user.can() 和current_user.is_administrator()。
    否则如果不先检查用户是否登录就调用权限检查函数，就会报错
    """

    def can(self, permissions):
        """
        :summary: 检查匿名用户是否具有指定的权限，直接返回False
        :param permissions:
        :return:
        """
        return False

    def is_administrator(self):
        """
        :summary: 检查匿名用户是否具有指定的权限，直接返回False
        :return:
        """
        return False


login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    """
    用户角色模型
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """
        :summary: 插入用户角色
        :return:
        """
        roles = {
            'User': (
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLE, True),
            'Moderator': (
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLE |
                Permission.MODERATE_COMMENTS, False),
            'Administrator': (Permission.ADMINISTER, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Post(db.Model):
    """
    文章模型
    """
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, index=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def create_fake(count=100):
        """
        :summary: 创建虚拟的文章
        :param count:
        :return:
        """
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(
                body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                timestamp=forgery_py.date.date(True),
                author=u
            )
            db.session.add(p)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    """
    comments model
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

# -*- coding: utf-8 -*-
from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach


class Permission:
    FOLLOW = 0x01
    COMMENTS = 0x02
    WRITE_ARTICLES = 0x03
    MODERATE_COMMENTS = 0x10
    ADMINISTRATOR = 0xff


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    real_name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __init__(self, **kwargs):
        # 先调用基类的构造函数
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    # 设置password的只写不可读属性
    @property
    def password(self, password):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 检验密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    # 生成账户确认令牌
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # 验证账户确认令牌
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except ValueError:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 生成重设密码确认令牌
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset':self.id})

    # 验证重设密码确认令牌
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except ValueError:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    # 角色验证
    def can(self, permissions):
        return self.role is not None \
               and (self.role.permissions & permissions) == permissions

    # 管理员验证
    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    # 生成虚拟用户
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            user = User(
                email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                real_name=forgery_py.name.full_name(),
                location=forgery_py.address.city(),
                about_me=forgery_py.lorem_ipsum.sentence(),
                member_since=forgery_py.date.date(True)
                )
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def create_roles():
        roles = {
            'User': (Permission.FOLLOW|Permission.COMMENTS|Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW|Permission.COMMENTS|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.default = roles[r][1]
            role.permissions = roles[r][0]
            db.session.add(role)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    # 博客文章包含内容，作者，时间戳
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # 一个作者对应多篇文章，因此在多的这一侧建立外键
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 转换文章，on_changed_body函数自动把body字段中的文本渲染成html格式
    # 真正的转换过程分为三步，如下：
    # 首先markdown()把文本转化为html
    # 然后把得到的结果和允许使用的HTml标签列表传给clean函数，clean删除所有不在白名单中的标签
    # 最后一步由linkify完成，把纯文本中的URL转换成<a>链接
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags,
            strip=True
        ))

    # 生成虚拟文章
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            user = User.query.offset(randint(0, user_count-1)).first()
            post = Post(
                body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                timestamp=forgery_py.date.date(True),
                author=user
             )
            db.session.add(post)
            db.session.commit()

# on_changed_body()方法注册在SQLAlchemy的"set"事件监听程序上
# 这意味着只要body这个字段设置了新值，函数就会被自动调用
db.event.listen(Post.body, 'set', Post.on_changed_body)

# 使用flask-login扩展必须提供的回调函数
# 用于从会话中存储的ID加载用户对象
# 接收一个用户id作为输入，返回相应的用户对象
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



























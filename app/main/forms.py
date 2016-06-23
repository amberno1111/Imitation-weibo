from flask_wtf import Form
from wtforms import SubmitField, StringField, TextAreaField, BooleanField, SelectField
from wtforms import ValidationError
from wtforms.validators import Length, DataRequired, Email, Regexp
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class EditProfileForm(Form):
    real_name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('所在城市', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('更新我的资料')


class EditProfileAdminForm(Form):
    email = StringField('邮件', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(
        '昵称',
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                '^[A-Za-z][A-Za-z0-9]*$',
                0,
                '用户名必须是字母、数字')
        ])
    confirmed = BooleanField('账户确认')
    real_name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('所在城市', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    role = SelectField('角色', coerce=int)
    submit = SubmitField('更新资料')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if self.user.email != field.data and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')

    def validate_username(self, field):
        if self.user.username != field.data and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册')


class PostForm(Form):
    body = PageDownField('有什么新鲜事想告诉大家？', validators=[DataRequired()])
    submit = SubmitField('发布')

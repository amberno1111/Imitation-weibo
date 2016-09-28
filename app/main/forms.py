# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired


class PostForm(Form):
    """
    发表微博表单
    """
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('发布微博')


class CommentForm(Form):
    """	CommentForm	"""
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('发布评论')

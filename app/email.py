# -*- coding: utf-8 -*-
from flask_mail import Message
from threading import Thread
from app import mail
from flask import render_template, current_app


def send_async_email(app, message):
    # FlaskMail中的send()函数使用current_app，因此必须激活程序上下文
    # 但是在不同的线程中使用时，必须使用app.app_context()人工创建程序上下文
    with app.app_context():
        mail.send(message=message)


def send_email(recipient, subject, template, **kwargs):
    """
    :summary: 发送异步邮件
    :param recipient: 收件人
    :param subject: 邮件主题
    :param template: 邮件模板
    :param kwargs: 其他参数
    :return:
    """
    # 获取真正的程序对象
    app = current_app._get_current_object()
    message = Message(
        recipients=[recipient],
        subject=app.config['EMAIL_PREFIX'] + ' ' + subject)
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=(app, message))
    thr.start()
    return thr

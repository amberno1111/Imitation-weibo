from flask import render_template, current_app
from flask_mail import Message
from threading import Thread
from app import mail


def async_send_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        app.config['EMAIL_PREFIX'] + ' ' + subject,
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=async_send_email, args=[app, msg])
    thr.start()
    return thr

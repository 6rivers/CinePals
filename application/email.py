from flask_mail import Message
from application import app, mail
from flask import render_template
from threading import Thread


def send_async_email(app, msg):

    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # creating a thread and assigning a task(function) with two arguments
    Thread(target=send_async_email, args=(app, msg)).start()


def send_reset_password_email(user):
    token = user.get_reset_password_token()
    text_body = render_template(
        'reset_password_email.txt', user=user, token=token)
    html_body = render_template(
        'reset_password_email.html', user=user, token=token)
    send_email('CinePals Reset Password',
               sender=app.config['ADMINS'][0], recipients=[user.email], text_body=text_body, html_body=html_body)

from flask import Flask
from application.config import Config
# Flask client for OAuth
# Authlib is the Python library in building OAuth and OpenID Connect servers
from authlib.integrations.flask_client import OAuth
# Flask client for SQLAlchemy., which translates Python classes to tables on relational databases and automatically converts function calls to SQL statements
from flask_sqlalchemy import SQLAlchemy
# Flask extension to find and apply changes to DB from models
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os

application = Flask(__name__)

app = application

app.config.from_object(Config)

social_oauth = OAuth(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'index'
mail = Mail(app)

if not app.debug:

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

#     # ...
#     # if app.config['LOG_TO_STDOUT']:
#     #     stream_handler = logging.StreamHandler()
#     #     stream_handler.setLevel(logging.INFO)
#     #     app.logger.addHandler(stream_handler)

#     if app.config['LOG_WITH_GUNICORN']:
#         gunicorn_error_logger = logging.getLogger('gunicorn.error')
#         app.logger.handlers.extend(gunicorn_error_logger.handlers)
#         app.logger.setLevel(logging.DEBUG)

#     else:
#         if not os.path.exists('logs'):
#             os.mkdir('logs')
#         file_handler = RotatingFileHandler('logs/cinepals.log', maxBytes=10240,
#                                            backupCount=10)
#         file_handler.setFormatter(logging.Formatter(
#             '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#         file_handler.setLevel(logging.INFO)
#         app.logger.addHandler(file_handler)
#     if app.config['MAIL_SERVER']:
#         auth = None
#         if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
#             auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
#         secure = None
#         if app.config['MAIL_USE_TLS']:
#             secure = ()
#         mail_handler = SMTPHandler(
#             mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
#             fromaddr=app.config['ADMINS'][0],
#             toaddrs=app.config['ADMINS'][0], subject='CinePals Failure',
#             credentials=auth, secure=secure)
#         mail_handler.setLevel(logging.ERROR)
#         app.logger.addHandler(mail_handler)

#     app.logger.setLevel(logging.INFO)
#     app.logger.info('CinePals startup')


from application import routes, models, errors

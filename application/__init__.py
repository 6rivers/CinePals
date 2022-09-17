from flask import Flask
from application.config import Config
# Flask client for OAuth
from authlib.integrations.flask_client import OAuth
# Flask client for SQLAlchemy., which translates Python classes to tables on relational databases and automatically converts function calls to SQL statements
from flask_sqlalchemy import SQLAlchemy
# Flask extension to find and apply changes to DB from models
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import logging
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

if app.debug:

    # ...
    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/cinepals.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('CinePals startup')


from application import routes, models, errors

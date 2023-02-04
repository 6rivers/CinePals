import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tough-to-guess'
    OAUTH_CREDENTIALS = {
        'google': {
            'id': os.environ.get('GOOGLE_ID'),
            'secret': os.environ.get('GOOGLE_SECRET')
        }
    }
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'site.db')
    # LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    # LOG_WITH_GUNICORN = os.getenv('LOG_WITH_GUNICORN', default=False)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['admin@ranganaths.com']

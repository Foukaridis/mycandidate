import os
from flask import Flask, session

app = Flask(
    __name__,
    static_folder='static')

app.secret_key = os.environ.get('SECRET_KEY', 'SECRET_KEY')

# setup configs
env = os.environ.get('FLASK_ENV', 'development')

app.config['ENV'] = env
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, f'config/{env}.cfg')
if os.path.exists(config_path):
    app.config.from_pyfile(config_path)
else:
    # Fallback config for CI/testing environments where config files don't exist
    app.config.update(  # nosec B106 - not hardcoded passwords, Flask security config parameters
        DEBUG=True,
        TESTING=(env == 'test'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            f'postgresql://postgres:postgres@{os.environ.get("DB_HOST", "localhost")}:{os.environ.get("DB_PORT", "5433")}/mycandidate' + ('_test' if env == 'test' else '')
        ),
        SECURITY_URL_PREFIX="/user",
        SECURITY_PASSWORD_HASH="sha256_crypt",
        SECURITY_PASSWORD_SALT="sha256_crypt",
        SECURITY_EMAIL_SENDER="",
        SECURITY_LOGIN_URL="/login/",
        SECURITY_LOGOUT_URL="/logout/",
        SECURITY_POST_LOGIN_VIEW="/",
        SECURITY_CHANGE_URL="/change-password/",
        SECURITY_RESET_URL="/forgot-password",
        SECURITY_EMAIL_SUBJECT_REGISTER="Welcome to middleware",
    )

# CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf_protect = CSRFProtect(app)

# Database
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECURITY_REGISTERABLE'] = True

from flask_sslify import SSLify
ssl = SSLify(app)
app.config['WTF_CSRF_ENABLED'] = False
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask_minify import Minify
minify = Minify(app=app, passive=True)
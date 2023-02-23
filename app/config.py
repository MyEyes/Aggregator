import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLITE_FALLBACK = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lol-so-secret'
    if SECRET_KEY == "CHANGEME":
        raise Exception("Change the secret key you wombat")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'aggregate.db') if SQLITE_FALLBACK else 'mysql://127.0.0.1:3306'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_PAGE_SIZE=20
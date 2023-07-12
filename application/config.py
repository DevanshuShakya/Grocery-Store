import os
current_dir=os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(current_dir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "groceryshopdb.sqlite3")
    DEBUG = True
    SECRET_KEY = 'secret-key-goes-here'
    SECURITY_PASSWORD_HASH="bcrypt"
    SECURITY_PASSWORD_SALT="really super secret"
    SECURITY_REGISTERABLE=True
    SECURITY_SEND_REGISTER_EMAIL=True
    SECURITY_UNAUTHORIZED_VIEW=None
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS= True
    MAIL_USERNAME = 'ticketshownow@gmail.com'
    MAIL_PASSWORD = 'frprtksngzetxfym'
    # SECURITY_CHANGE_URL='/change'
    SECURITY_RECOVERABLE=True
    


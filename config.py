class Config(object):
    DEBUG = True
    THREADED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.sqlite3'
	SECRET_KEY = "random string"
	SQLALCHEMY_TRACK_MODIFICATIONS = True

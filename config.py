import os

DIALECT = 'postgresql'
DRIVER = 'psycopg2'
USERNAME = 'postgres'
PASSWORD = 'mujianan'
HOST = 'localhost'
PORT = 5432
DATABASE = 'movies'


class Config:
    SECRET_KEY = os.getenv("VOTE_SECRET_WORK_KEY") or 'very hard to get secret key'
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}".format(
            DIALECT,
            DRIVER,
            USERNAME,
            PASSWORD,
            HOST,
            PORT,
            DATABASE
        )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}".format(
            DIALECT,
            DRIVER,
            USERNAME,
            PASSWORD,
            HOST,
            PORT,
            DATABASE
        )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}".format(
            DIALECT,
            DRIVER,
            USERNAME,
            PASSWORD,
            HOST,
            PORT,
            DATABASE
        )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

config = {
    'developments': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

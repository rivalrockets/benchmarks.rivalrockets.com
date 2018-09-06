from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from config import config

# need to set SQLAlchemy's metadata up so that all the things have names!
# otherwise Alembic's voodoo autogenerate approach won't work with SQLite!
# http://alembic.zzzcomputing.com/en/latest/naming.html#autogen-naming-conventions
meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

db = SQLAlchemy(metadata=meta)


def create_app(config_name):
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    # This is where the routes would be registered, blueprints are ideal.

    from .api_1_0 import api_blueprint as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app

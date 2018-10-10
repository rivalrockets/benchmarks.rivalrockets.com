import os
from app import create_app, db
from app.models import User, Machine, Revision, Role, RevokedToken
from flask_migrate import Migrate
import click
from flask_jwt_extended import JWTManager

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

jwt = JWTManager(app)
migrate = Migrate(app, db)



# Why does this need to be here? I want to put this in authentication.
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Machine=Machine,
                Revision=Revision, Role=Role)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade

    # migrate database to latest Revision
    upgrade()

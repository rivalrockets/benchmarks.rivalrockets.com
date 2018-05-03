import os
from app import create_app, db
from app.models import User, Machine, Revision
from flask_migrate import Migrate
import click

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Machine=Machine,
                Revision=Revision)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade

    # migrate database to latest Revision
    upgrade()

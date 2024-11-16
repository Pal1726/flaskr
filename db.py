import click
from flask import current_app, g
from . import db

def get_db():
    """Get a database connection."""
    return db.session  # Using the SQLAlchemy session

def close_db(e=None):
    """Close the database session."""
    db.session.remove()  # Automatically remove the session

def init_db():
    """Initialize the database."""
    db.create_all()  # Create all tables based on models

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Initialize the app with database commands."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# import sqlite3

# import click
# from flask import current_app, g


# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row

#     return g.db


# def close_db(e=None):
#     db = g.pop('db', None)

#     if db is not None:
#         db.close()

# def init_db():
#     db = get_db()

#     with current_app.open_resource('schema.sql') as f:
#         db.executescript(f.read().decode('utf8'))


# @click.command('init-db')
# def init_db_command():
#     """Clear the existing data and create new tables."""
#     init_db()
#     click.echo('Initialized the database.')

# def init_app(app):
#     app.teardown_appcontext(close_db)
#     app.cli.add_command(init_db_command)
import mysql.connector
from flask import current_app, g
import click

def get_db():
    """Get the database connection from the Flask app's global context."""
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],  # Updated from DB_HOST to MYSQL_HOST
            user=current_app.config['MYSQL_USER'],  # Updated from DB_USER to MYSQL_USER
            password=current_app.config['MYSQL_PASSWORD'],  # Updated from DB_PASSWORD to MYSQL_PASSWORD
            database=current_app.config['MYSQL_DB']  # Updated from DB_NAME to MYSQL_DB
        )
    return g.db

def get_db_cursor(dictionary=False):
    """Get a database cursor, with an option to return results as dictionaries."""
    db = get_db()
    return db.cursor(dictionary=dictionary)

def close_db(e=None):
    """Close the database connection if it's open."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database by reading the schema from schema.sql."""
    db = get_db()
    cursor = db.cursor()

    try:
        # Read schema from schema.sql and execute it
        with current_app.open_resource('schema.sql') as f:
            sql_script = f.read().decode('utf8')
            # Execute SQL script
            for statement in sql_script.split(';'):
                if statement.strip():  # Check if the statement is not empty
                    cursor.execute(statement)
        
        db.commit()  # Commit after executing all statements
    except Exception as e:
        db.rollback()  # Rollback on error
        print(f"Error during database initialization: {e}")
    finally:
        cursor.close()  # Ensure cursor is closed

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Initialize the app with necessary functions and commands."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

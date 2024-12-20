##1. with sqlite

# import os

# from flask import Flask


# def create_app(test_config=None):
#     # create and configure the app
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_mapping(
#         SECRET_KEY='dev',
#         DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
#     )

#     if test_config is None:
#         # load the instance config, if it exists, when not testing
#         app.config.from_pyfile('config.py', silent=True)
#     else:
#         # load the test config if passed in
#         app.config.from_mapping(test_config)

#     # ensure the instance folder exists
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass

#     # a simple page that says hello
#     # @app.route('/hello')
#     # def hello():
#     #     return 'Hello, World!'

#     from . import db
#     db.init_app(app)

#     from . import auth
#     app.register_blueprint(auth.bp)


#     from . import blog
#     app.register_blueprint(blog.bp)
#     app.add_url_rule('/', endpoint='index')


#     return app

#2. with mysql connector
import os
from flask import Flask
from mysql import connector
from mysql.connector import Error

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MYSQL_HOST='localhost',  # Change to your MySQL host
        MYSQL_USER='root',  # Change to your MySQL username
        MYSQL_PASSWORD='Rathi@123',  # Change to your MySQL password
        MYSQL_DB='first_project',  # Change to your database name
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app


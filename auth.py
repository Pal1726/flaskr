# import functools

# from flask import (
#     Blueprint, flash, g, redirect, render_template, request, session, url_for
# )
# from werkzeug.security import check_password_hash, generate_password_hash

# from flaskr.db import get_db

# bp = Blueprint('auth', __name__, url_prefix='/auth')
# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         import pdb; pdb.set_trace()
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'

#         if error is None:
#             try:
#                 db.execute(
#                     "INSERT INTO user (username, password) VALUES (?, ?)",
#                     (username, generate_password_hash(password)),
#                 )
#                 db.commit()
#             except db.IntegrityError:
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for("auth.login"))

#         flash(error)

#     return render_template('auth/register.html')

# @bp.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None
#         user = db.execute(
#             'SELECT * FROM user WHERE username = ?', (username,)
#         ).fetchone()

#         if user is None:
#             error = 'Incorrect username.'
#         elif not check_password_hash(user['password'], password):
#             error = 'Incorrect password.'

#         if error is None:
#             session.clear()
#             session['user_id'] = user['id']
#             return redirect(url_for('index'))

#         flash(error)

#     return render_template('auth/login.html')

# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()

# @bp.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))

# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))

#         return view(**kwargs)

#     return wrapped_view

import functools
import mysql.connector  # Ensure this is imported
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db_cursor  # Import your cursor function
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            cursor = get_db_cursor()  # Get cursor from get_db_cursor
            try:
                cursor.execute(
                    "INSERT INTO user (username, password) VALUES (%s, %s)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except mysql.connector.IntegrityError:
                error = f"User {username} is already registered."
            except Exception as e:
                print(f"Error during registration: {e}")
                flash('An error occurred while registering the user.')
            finally:
                cursor.close()  # Ensure cursor is closed

            if error is None:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        cursor = get_db_cursor()  # Get cursor from get_db_cursor
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        user = cursor.fetchone()  # Fetch the user

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):  # user[2] is the password column
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]  # user[0] is the id column
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cursor = get_db_cursor(dictionary=True)  # Use get_db_cursor
        cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
        g.user = cursor.fetchone()  # Fetch the user
        cursor.close()  # Close the cursor after fetching the user

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

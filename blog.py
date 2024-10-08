# from flask import (
#     Blueprint, flash, g, redirect, render_template, request, url_for
# )
# from werkzeug.exceptions import abort

# from flaskr.auth import login_required
# from flaskr.db import get_db

# bp = Blueprint('blog', __name__)

# @bp.route('/')
# def index():
#     db = get_db()
#     posts = db.execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' ORDER BY created DESC'
#     ).fetchall()
#     return render_template('blog/index.html', posts=posts)

# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO post (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/create.html')

# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")

#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)

#     return post

# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/update.html', post=post)

# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM post WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('blog.index')) 

import functools
import mysql.connector  # Ensure this is imported
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    try:
        cursor.execute(
            'SELECT p.id, title, body, created, author_id, username '
            'FROM post p JOIN user u ON p.author_id = u.id '
            'ORDER BY created DESC'
        )
        posts = cursor.fetchall()  # Fetch all posts as dictionaries
    except Exception as e:
        print(f"Error fetching posts: {e}")
        posts = []  # Fallback to an empty list on error
    finally:
        cursor.close()  # Ensure cursor is closed

    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()  # Store the cursor
            try:
                cursor.execute(
                    'INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)',
                    (title, body, g.user['id'])  # Access user id by field name
                )
                db.commit()
                return redirect(url_for('blog.index'))
            except mysql.connector.Error as e:  # Handle MySQL errors
                print(f"Error creating post: {e}")
                flash('An error occurred while creating the post. Please try again.')
            except Exception as e:
                print(f"General error creating post: {e}")
                flash('An unexpected error occurred.')
            finally:
                cursor.close()  # Ensure cursor is closed

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    db = get_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    try:
        cursor.execute(
            'SELECT p.id, title, body, created, author_id, username '
            'FROM post p JOIN user u ON p.author_id = u.id '
            'WHERE p.id = %s',
            (id,)
        )
        post = cursor.fetchone()

        if post is None:
            abort(404, f"Post id {id} doesn't exist.")

        if check_author and post['author_id'] != g.user['id']:  # Access by field name
            abort(403)

        return post
    finally:
        cursor.close()  # Ensure cursor is closed

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()  # Store the cursor
            try:
                cursor.execute(
                    'UPDATE post SET title = %s, body = %s WHERE id = %s',
                    (title, body, id)
                )
                db.commit()
                return redirect(url_for('blog.index'))
            except mysql.connector.Error as e:  # Handle MySQL errors
                print(f"Error updating post: {e}")
                flash('An error occurred while updating the post. Please try again.')
            except Exception as e:
                print(f"General error updating post: {e}")
                flash('An unexpected error occurred.')
            finally:
                cursor.close()  # Ensure cursor is closed

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    cursor = db.cursor()  # Store the cursor
    try:
        cursor.execute('DELETE FROM post WHERE id = %s', (id,))
        db.commit()
    except mysql.connector.Error as e:  # Handle MySQL errors
        print(f"Error deleting post: {e}")
        flash('An error occurred while deleting the post.')
    except Exception as e:
        print(f"General error deleting post: {e}")
        flash('An unexpected error occurred.')
    finally:
        cursor.close()  # Ensure cursor is closed

    return redirect(url_for('blog.index'))

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
    posts = db.execute(
        'SELECT p.id, body, tag, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/<string:tag>/tag')
def tag(tag):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, body, tag, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE tag = ?'
        ' ORDER BY created DESC',
        (tag,)
    ).fetchall()
    return render_template('blog/tag.html', posts=posts, tag=tag)

@bp.route('/<int:id>/mypage')
def mypage(id):
    db = get_db()

    user = db.execute(
        'SELECT id, username, profession'
        ' FROM user'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    posts = db.execute(
        'SELECT p.id, body, tag, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.author_id = ?'
        ' ORDER BY created DESC',
        (id,)
    ).fetchall()
    return render_template('blog/mypage.html', user=user, posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        body = request.form['body']
        tag = request.form['tag']
        error = None

        #if not title:
        #    error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (body, tag, author_id)'
                ' VALUES (?, ?, ?)',
                (body, tag, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, body, tag, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        body = request.form['body']
        tag = request.form['tag']
        error = None

        #if not title:
        #    error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET body = ?, tag = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

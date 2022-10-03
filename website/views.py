import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from website import create_app
from . import db
from .models import Post, User, Comment, Like, Reply

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template('profile.html', user=user, posts=posts, username=username)


@views.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        profile_photo = request.files['profile-photo']
        user_name = request.form.get('name')
        user_last_name = request.form.get('last-name')
        about_user = request.form.get('about')
        occupation = request.form.get('occupation')

        if not user_name or not user_last_name:
            flash('Fields "Name" and "Last name" cannot be empty', category='error')
        else:
            if 'profile-photo' in request.files:
                photo_path = os.path.join(create_app().config['UPLOAD_FOLDER'], profile_photo.filename)
                profile_photo.save(photo_path)
                user = User.query.filter_by(username=current_user.username).first()
                user.name = user_name
                user.last_name = user_last_name
                user.profile_photo_path = photo_path
                user.occupation = occupation
                if about_user:
                    user.about_user = about_user
                db.session.commit()
                return redirect(url_for('views.profile', username=current_user.username))
    return render_template('edit_profile.html', user=current_user)


@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        text = request.form.get('text')
        file1 = request.files['file1']

        if not text:
            flash('Post cannot be empty', category='error')
        elif not title:
            flash('Post cannot be without title', category='error')
        elif 'file1' not in request.files:
            flash('Add photo to post', category='error')
        else:
            path = os.path.join(create_app().config['UPLOAD_FOLDER'], file1.filename)
            file1.save(path)
            post = Post(title=title, text=text, author=current_user.id, photo_path=path)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))
    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Post does not exist.', category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category='success')

    return redirect(url_for('views.home'))


@views.route("/edit-post/<id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    if request.method == 'POST':
        post = Post.query.filter_by(id=id, author=current_user.id).first()
        photo = request.files['edited-photo']

        if not post:
            flash('Post does not exist', category='error')
        # elif current_user.id != post.id:
        #     flash('You do not have permission to edit this post', category='error')
        else:
            if not photo:
                post.title = request.form.get('edited-title')
                post.text = request.form.get('edited-text')
                db.session.commit()
                return redirect(url_for('views.home'))
            else:
                path = os.path.join(create_app().config['UPLOAD_FOLDER'], photo.filename)
                photo.save(path)
                post.photo_path = path
                post.title = request.form.get('edited-title')
                post.text = request.form.get('edited-text')
                db.session.commit()
                return redirect(url_for('views.home'))

    post = Post.query.filter_by(id=id, author=current_user.id).first()
    return render_template('edit_post.html', user=current_user, post=post)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('comment')

    if not text:
        flash('Comment can not be empty', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')
    return redirect(url_for('views.home'))


@views.route('/reply-comment/<comment_id>', methods=['POST'])
@login_required
def reply_comment(comment_id):
    text = request.form.get('reply')

    if not text:
        flash('Reply can not be empty', category='error')
    else:
        comment = Comment.query.filter_by(id=comment_id)
        if comment:
            reply = Reply(text=text, author=current_user.id, comment_id=comment_id)
            db.session.add(reply)
            db.session.commit()
        else:
            flash('Comment does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/delete-reply/<reply_id>')
@login_required
def reply_delete(reply_id):
    reply = Reply.query.filter_by(id=reply_id).first()

    if not reply:
        flash('Reply does not exist.', category='error')
    elif current_user.id != reply.author and current_user.id != reply.comment_id.author:
        flash('You do not have permission to delete this comment', category='error')
    else:
        db.session.delete(reply)
        db.session.commit()

    return redirect((url_for('views.home')))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from forms import RegisterForm, LoginForm, PostForm
from models import User, Post

@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Authenticated users already have an account context; keep them out of
        # registration so they do not accidentally create duplicate identities.
        return redirect(url_for('home'))

    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()

        if existing_user:
            # Check username and email together to preserve both uniqueness
            # guarantees before attempting to commit the new user.
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data)

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')

            # Flask-Login stores the originally requested protected URL in
            # "next"; honoring it keeps login from breaking the user's flow.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        # Use current_user instead of a submitted user id so clients cannot
        # create posts under another account.
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )

        db.session.add(post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', form=form)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route('/delete-post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        # The route is authenticated, but ownership is the authorization check
        # that prevents one signed-in user from deleting another user's post.
        flash('You cannot delete this post.', 'danger')
        return redirect(url_for('home'))

    db.session.delete(post)
    db.session.commit()

    flash('Post deleted successfully.', 'success')
    return redirect(url_for('home'))

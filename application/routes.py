from application import app, db
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from application.forms import RegisterForm, LoginForm, CreateGroupForm, SearchMovieForm, ResetPasswordRequestForm, ResetPasswordForm
from application.social import OAuthSignIn
from application.functions import search_movies, get_movie_details, get_group_movies, get_wa_link
from application.models import User, Group, Clubs, Movie, MovieGroups, Review
from application.email import send_reset_password_email
import secrets
import random


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    next_page = request.args.get('next')
    if next_page is not None and next_page.find('invite/'):
        session['next_url'] = next_page
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Username or password is incorrect', category='error')
            return redirect(url_for('index'))
        login_user(user, remember=form.remember.data)
        next_url = session['next_url']
        if next_url is not None and next_url.find('invite/'):
            session['next_url'] = None
            return redirect(next_url)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            flash(f'Welcome back {user.name}!', category='success')
            return redirect(url_for('home'))
        flash(f'Welcome back {user.name}!', category='success')
        return redirect(next_page)

    return render_template('index.html', title='Index', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        name = form.name.data.lower()
        number = str(random.randint(1111, 9999))
        username = name + number
        user = User(email=email, name=name, username=username)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Hello {name}, an account has been created for you, please Login to continue",
              category='success')
        return redirect(url_for('index'))

    return render_template('register.html', title='Register', form=form)


@app.route('/oauth_authorize/<provider>')
def oauth_authorize(provider):
    # This takes the appropriate Sub Class based on provider(fb/google) and
    # registers via app_auth and all required parameters like apis, IDs, secrets
    authentication = OAuthSignIn.get_provider(provider)
    # This calls the authorize function in respective subclass and redirect the user
    # to Auth provider for authentication
    # it also carries the callback URL to the Auth provider
    return authentication.authorize()


@app.route('/oauth_callback/<provider>')
def oauth_callback(provider):
    # since we have given Pre-specified URL (/callback/fb/ or /callback/google/)
    # during the auth process as shown above, the Auth provider redirects the user
    # back to this URL after sigin process. So we have <provider> as a variable(dynamic URL)
    # and based on that we pass the variable to below statement to get the
    # appropriate subclass and calls the .callback() function within that subclass
    # to take the authentication code that comes in the callback URL and asks for
    # access token and then asks for user info
    authentication = OAuthSignIn.get_provider(
        provider)
    name, email, social_id, picture = authentication.callback()
    if social_id is None:
        flash('Authentication failed.', category='error')
        return redirect(url_for('index'))
    user = User.query.filter_by(email=email).first()
    if user:
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            flash(f'Welcome back {user.name}!', category='success')
            return redirect(url_for('home'))
        flash(f'Welcome back {user.name}!', category='success')
        return redirect(next_page)
    else:
        user = User(name=name, email=email,
                    social_id=social_id, username=social_id, picture=picture)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            flash(f'Welcome {user.name}!', category='success')
            return redirect(url_for('home'))
        flash(f'Welcome {user.name}!', category='success')
        return redirect(next_page)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user and not user.social_id:
            send_reset_password_email(user)
        flash(
            f"Please check your Email for instructions to reset Password", category="info")
        return redirect(url_for('index'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(f"Your password has been updated successfully, Please login to continue",
              category="success")
        return redirect(url_for('index'))
    return render_template('reset_password.html', title='Update Password', form=form)


@app.route('/updatepassword/<username>', methods=['GET', 'POST'])
@login_required
def updatepassword(username):
    form = ResetPasswordForm()
    if current_user.username == username:
        if form.validate_on_submit():
            user = current_user
            if not user.social_id:
                user.set_password(form.password.data)
                db.session.commit()
                flash(f"Your password has been updated successfully",
                      category="success")
                return redirect(url_for('profile', username=user.username))
    return render_template('reset_password.html', title='Update Password', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = CreateGroupForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.desc.data
        owner_id = current_user.id
        invite_token = secrets.token_hex(10)
        group = Group(name=name, description=description,
                      owner_id=owner_id, invite_token=invite_token)
        db.session.add(group)
        db.session.commit()
        group = Group.query.filter_by(invite_token=invite_token).first()
        club = Clubs(club_user=current_user, club_group=group)
        db.session.add(club)
        db.session.commit()
        return redirect(url_for('group', group_id=invite_token))
    groups = current_user.all_groups().all()
    return render_template('home.html', title='Home', form=form, groups=groups)


@app.route('/group/<group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    group = Group.query.filter_by(invite_token=group_id).first()
    token = group.get_invite_user_token()
    wa_link = get_wa_link(token)
    user_id = current_user.id
    check_user = group.group_users.filter_by(user_id=user_id).first()
    if not check_user:
        return redirect(url_for('index'))

    if group:
        form = SearchMovieForm()
        # group_name = name
        if form.validate_on_submit():
            movie_name = form.name.data
            return redirect(url_for('search', group_id=group_id, name=movie_name))
    else:
        flash(f"Group not found", category='error')
        return redirect(url_for('home'))
    results = get_group_movies(group_id)
    reviews = Review.query.filter_by(group_id=group.id).all()
    all_users = group.all_users().all()
    return render_template('group.html', title='Group', form=form, reviews=reviews, movies=results, group=group, wa_link=wa_link, users=all_users)


@app.route('/removeuser/<group_id>/<username>')
@login_required
def removeuser(group_id, username):
    group = Group.query.filter_by(invite_token=group_id).first()
    user = User.query.filter_by(username=username).first()
    # Only if user is not the owner of the group
    if group.owner.id != user.id:
        assoc = Clubs.query.filter_by(
            club_user=user, club_group=group).first()
        db.session.delete(assoc)
        db.session.commit()
        return redirect(url_for('group', group_id=group.invite_token))


@app.route('/deletegroup/<group_id>')
@login_required
def deletegroup(group_id):
    group = Group.query.filter_by(invite_token=group_id).first()
    if group.owner_id == current_user.id:
        MovieGroups.query.filter_by(group_id=group.id).delete()
        Clubs.query.filter_by(group_id=group.id).delete()
        db.session.delete(group)
        db.session.commit()
        flash("Your group has been deleted", category='info')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route('/search/<group_id>/<name>')
@login_required
def search(group_id, name):
    results = search_movies(name)
    group = Group.query.filter_by(invite_token=group_id).first()
    group_id = group.invite_token

    return render_template('searchresults.html', title='Search Results', movies=results, group_id=group_id)


@app.route('/invite/<token>')
@login_required
def invite(token):
    group = Group.verify_invite_user_token(token)
    if group:
        group_id = group.id
        user = current_user.user_groups.filter_by(group_id=group_id).first()
        if user:
            flash('Welcome back!', category='success')
            return redirect(url_for('group', group_id=group.invite_token))
        else:
            assoc = Clubs(club_user=current_user, club_group=group)
            db.session.add(assoc)
            db.session.commit()
            flash(f"You are now part of this group", category='info')
            return redirect(url_for('group', group_id=group.invite_token))


@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    groups = None
    if user == current_user:
        groups = Group.query.filter_by(owner_id=user.id).all()
    print(groups)
    return render_template('profile.html', title='Profile', groups=groups, user=user)


@app.route('/add_movie/<group_id>/<imdb_id>')
@login_required
def add_movie(group_id, imdb_id):
    movie = Movie.query.filter_by(imdb_id=imdb_id).first()
    if not movie:
        name, cover_url, plot, genre = get_movie_details(imdb_id)
        movie = Movie(name=name, imdb_id=imdb_id,
                      cover_url=cover_url, plot=plot, genre=genre)
        db.session.add(movie)
        db.session.commit()
    movie = Movie.query.filter_by(imdb_id=imdb_id).first()
    group = Group.query.filter_by(invite_token=group_id).first()
    movie_in_group = MovieGroups.query.filter_by(
        group_id=group.id, movie_id=movie.id).first()
    if movie_in_group:
        flash(f"This movie is already been added to your group", category='info')
        return redirect(url_for('group', group_id=group_id))
    assoc = MovieGroups(m_movie=movie, g_group=group)
    db.session.add(assoc)
    db.session.commit()
    flash(f"Movie added to this group", category='success')
    return redirect(url_for('group', group_id=group_id))


@app.route('/delete_movie/<group_id>/<imdb_id>')
@login_required
def delete_movie(group_id, imdb_id):
    movie = Movie.query.filter_by(imdb_id=imdb_id).first()
    group = Group.query.filter_by(invite_token=group_id).first()
    movie_in_group = MovieGroups.query.filter_by(
        group_id=group.id, movie_id=movie.id).first()
    if movie_in_group:
        db.session.delete(movie_in_group)
        db.session.commit()
        flash(f"Movie deleted from this group", category='info')
        return redirect(url_for('group', group_id=group_id))
    else:
        return redirect(url_for('group', group_id=group_id))


@app.route('/add_review/<group_id>/<movie_id>', methods=['POST'])
@login_required
def add_review(group_id, movie_id):
    user_id = current_user.id
    group_id = group_id
    group = Group.query.get(group_id)
    group_token = group.invite_token
    movie = Movie.query.filter_by(imdb_id=movie_id).first()
    movie_id = movie.id
    review_text = request.form['ReviewText']
    rating = float(request.form['Rating'])
    review = Review(text=review_text, rating=rating, user_id=user_id,
                    movie_id=movie_id, group_id=group_id)
    db.session.add(review)
    db.session.commit()
    flash('Your review has been added', category='success')
    return redirect(url_for('group', group_id=group_token))

from application import db, app, login
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time
from flask_login import UserMixin
from hashlib import md5


class Clubs(db.Model):

    __tablename__ = "clubs"

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey(
        'group.id'), primary_key=True)

    club_user = db.relationship("User", back_populates='user_groups')
    club_group = db.relationship("Group", back_populates='group_users')

    def __repr__(self):
        return f"User and Groups {self.user_id} -- {self.group_id}"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(60))
    password_hash = db.Column(db.String(128))
    social_id = db.Column(db.String(60))
    picture = db.Column(db.String(240))
    user_groups = db.relationship(
        "Clubs", back_populates='club_user', lazy="dynamic")
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')
    owned_groups = db.relationship('Group', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f"Users {self.name}, {self.email}, {self.social_id}"

    def all_groups(self):
        following_groups = Group.query.join(
            Clubs, (Clubs.group_id == Group.id)).filter(Clubs.user_id == self.id)

        # own_posts = Post.query.filter_by(user_id=self.id)
        return following_groups

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[
                'HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    description = db.Column(db.String(240), unique=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    invite_token = db.Column(db.String(128))

    group_users = db.relationship(
        "Clubs", back_populates='club_group', lazy="dynamic")

    group_movies = db.relationship(
        "MovieGroups", back_populates='g_group', lazy="dynamic")

    def movies_list(self):

        return self.group_movies

    def all_users(self):
        users = User.query.join(
            Clubs, (Clubs.user_id == User.id)).filter(Clubs.group_id == self.id)

        # own_posts = Post.query.filter_by(user_id=self.id)
        return users

    def get_invite_user_token(self, expires_in=86400):
        return jwt.encode({'invite_token': self.invite_token, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_invite_user_token(token):
        try:
            invite_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[
                                      'HS256'])['invite_token']
        except:
            return
        return Group.query.filter_by(invite_token=invite_token).first()

    def __repr__(self):
        return f"Groups {self.name}, {self.owner_id}, {self.invite_token}"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(240), unique=False, nullable=False)
    imdb_id = db.Column(db.String(60), unique=True, nullable=False)
    cover_url = db.Column(db.String(360))
    plot = db.Column(db.String(360))
    genre = db.Column(db.String(20))

    movie_groups = db.relationship(
        "MovieGroups", back_populates='m_movie', lazy="dynamic")

    def __repr__(self):
        return f"Movies {self.name}, {self.imdb_id}"


class MovieGroups(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey(
        'movie.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey(
        'group.id'), primary_key=True)

    m_movie = db.relationship("Movie", back_populates='movie_groups')
    g_group = db.relationship("Group", back_populates='group_movies')

    def __repr__(self):
        return f"Movie Group :: {self.movie_id} - {self.group_id}"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(360), unique=False, nullable=True)
    rating = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def __repr__(self):
        return f"Users {self.text}, {self.movie_id}, {self.group_id}"

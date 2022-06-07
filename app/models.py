from app import db
from datetime import datetime
from geoalchemy2 import Geometry
from app import login
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False, unique=True)
    dob = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    tickets = db.Relationship("Ticket", backref="user", lazy=True)

    def set_password(self, password_input):
        self.password = generate_password_hash(password_input)

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))


class Cinema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    hotline = db.Column(db.String(20))
    geom = db.Column(Geometry("POINT"))
    movies = db.Relationship("Movie", backref="cinema", lazy=True)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    img = db.Column(db.String, nullable=False)
    describe = db.Column(db.Text)
    director = db.Column(db.String(50), nullable=False)
    cast = db.Column(db.Text, nullable=False)
    genre = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    running_time = db.Column(db.String(50), nullable=False)
    language = db.Column(db.Text)
    rated = db.Column(db.Text)
    cinema_id = db.Column(db.Integer, db.ForeignKey("cinema.id"), nullable=False)


class Movie_showtime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    screening_date = db.Column(db.String(50), nullable=False)
    time_start = db.Column(db.String(20))
    seats = db.Column(db.Integer)
    film_id = db.Column(db.Integer, primary_key=True)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)

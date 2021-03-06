from app import db
from geoalchemy2 import Geometry
from app import login
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String(10), nullable=False, unique=True)
    dob = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    tickets = db.relationship("Ticket", backref="users", lazy=True)

    def set_password(self, password_input):
        self.password = generate_password_hash(password_input)

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))


# movie_distributions = db.Table(
#     "movie_distributions",
#     db.Column("cinema_id", db.Integer, db.ForeignKey("cinemas.id"), primary_key=True),
#     db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True),
# )


class Cinema(db.Model):
    __tablename__ = "cinemas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # type = db.Column(db.String(25), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    hotline = db.Column(db.String(20))
    geom = db.Column(Geometry("POINT"))
    tickets = db.relationship("Ticket", backref="cinemas", lazy=True)

    # movie_distributions = db.relationship(
    #     "Movie",
    #     secondary=movie_distributions,
    #     lazy="subquery",
    #     backref=db.backref("cinemas", lazy=True),
    # )


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    img = db.Column(db.String, nullable=False)
    describe = db.Column(db.Text)
    director = db.Column(db.String(50), nullable=False)
    actor = db.Column(db.Text, nullable=False)
    genre = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.String(20), nullable=False)
    running_time = db.Column(db.String(50), nullable=False)
    language = db.Column(db.Text)
    rated = db.Column(db.Text)
    movie_showtimes = db.relationship("Movie_showtime", backref="movies", lazy=True)
    tickets = db.relationship("Ticket", backref="movies", lazy=True)


class Movie_showtime(db.Model):
    __tablename__ = "movie_showtimes"
    id = db.Column(db.Integer, primary_key=True)
    screening_date = db.Column(db.String(50), nullable=False)
    time_start = db.Column(db.String(20))
    seats = db.Column(db.Integer)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)
    tickets = db.relationship(
        "Ticket",
        backref="movie_showtimes",
        lazy=True,
    )


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    cinema_id = db.Column(db.Integer, db.ForeignKey("cinemas.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)
    movie_showtime_id = db.Column(
        db.Integer, db.ForeignKey("movie_showtimes.id"), nullable=False
    )

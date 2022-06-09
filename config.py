import os


class Config(object):
    # ...
    SECRET_KEY = os.environ.get("SECRET_KEY") or "cannot-be-guess"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:200420@localhost:5432/A-Nhom3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    print("Connect to database successfully!")

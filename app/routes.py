from app import app
from flask import render_template, request, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required

# from app import form
# from app.models import *
# from app.form import *


@app.route("/")
def hello_world():
    return "Hello, World!"

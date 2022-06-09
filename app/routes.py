import flask
from app import app
from app.models import *

from app import form
from app.form import *
from flask import request, render_template, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required


@app.route("/")
def index():
    return render_template("index.html", title="Trang chủ")


@app.route("/signUp", methods=["GET", "POST"])
def sign_up():
    # tạo biến form từ class SignUpForm bên form.py
    form = SignUpForm()
    if form.validate_on_submit():
        fullname = form.fullname.data
        email = form.email.data
        password = form.password.data
        phone_number = form.phone_number.data
        dob = form.dob.data
        gender = form.gender.data
        NewUser = User(
            fullname=fullname,
            email=email,
            password=password,
            phone_number=phone_number,
            dob=dob,
            gender=gender,
        )
        NewUser.set_password(password)
        db.session.add(NewUser)
        db.session.commit()
        flash("Đăng nhập ngay")
        return redirect(url_for("login", title="Đăng nhập"))
    return render_template("sign_up.html", form=form, title="Đăng kí người dùng")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Tài khoản hoặc mật khẩu chưa chính xác!")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)
        flash("Đăng nhập thành công")
        return redirect(url_for("index"))
    return render_template("login.html", title="Đăng nhập", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("Đăng xuất thành công")
    return redirect(url_for("index"))

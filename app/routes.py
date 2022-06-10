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
    form = SignUpUser()
    if form.validate_on_submit():
        fullname = form.fullname.data
        email = form.email.data
        password = form.password.data
        phone_number = form.phone_number.data
        dob = form.dob.data
        gender = form.gender.data
        new_user = User(
            fullname=fullname,
            email=email,
            password=password,
            phone_number=phone_number,
            dob=dob,
            gender=gender,
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Đăng nhập ngay")
        return redirect(url_for("login"))
    return render_template("sign_up.html", form=form, title="Đăng kí người dùng")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Nếu người dùng đã đăng nhập mà vào route này sẽ trả về index()
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # Nếu người dùng chưa đăng nhập mà vào route này sẽ trả về login.html
    form = LoginForm()
    if form.validate_on_submit():
        # Kiểm tra xem tên đăng nhập và mật khẩu có chính xác không
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Tài khoản hoặc mật khẩu chưa chính xác!")
            return redirect(url_for("login"))

        # Hàm lưu tên tài khoản khi đăng nhập thành công
        login_user(user, remember=form.remember_me.data)
        flash("Đăng nhập thành công!")
        return redirect(url_for("index"))
    return render_template("login.html", title="Đăng nhập", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("Đăng xuất thành công!")
    return redirect(url_for("index"))


@app.route("/manager/users")
@login_required
def users_manager():
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Only admin can access!")
        return redirect(url_for("index"))
    else:
        users = User.query.all()
        return render_template(
            "users_manager.html", users=users, title="Quản lý tài khoản người dùng"
        )


@app.route("/manager/user/delete/<int:id_user>")
def delete_user(id_user):
    user = User.query.get(id_user)
    db.session.delete(user)
    db.session.commit()
    flash("Xóa tài khoản thành công")
    return redirect(url_for("users_manager"))


@app.route("/manager/user/update/<int:id_user>", methods=["GET", "POST"])
def update_user(id_user):
    user = User.query.get(id_user)
    form = UpdateUser()
    if form.validate_on_submit():
        id_user = int(request.form.get("id_user"))
        user = User.query.get(id_user)
        user.fullname = form.fullname.data
        user.phone_number = form.phone_number.data
        user.dob = form.dob.data
        user.gender = form.gender.data
        is_admin = form.is_admin.data
        if is_admin == "True":
            new_is_admin = True
        else:
            new_is_admin = False
        user.is_admin = new_is_admin
        db.session.commit()
        flash("Cập nhật thông tin tài khoản thành công !")
        return redirect(url_for("users_manager"))
    return render_template(
        "update_user.html", user=user, form=form, title="Cập nhật thông tin tài khoản"
    )

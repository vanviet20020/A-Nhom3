# from crypt import methods
from turtle import title
from unicodedata import name
from app import app
from app.models import *
from app import form
from app.form import *
from flask import request, render_template, redirect, flash, url_for, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
import json


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


@app.route("/manager/user")
@login_required
def user_manager():
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        users = User.query.all()
        return render_template(
            "manager_user.html", users=users, title="Quản lý tài khoản người dùng"
        )


@app.route("/manager/user/delete/<int:id_user>")
def delete_user(id_user):
    user = User.query.get(id_user)
    db.session.delete(user)
    db.session.commit()
    flash("Xóa tài khoản thành công")
    return redirect(url_for("user_manager"))


@app.route("/manager/user/update/<int:id_user>", methods=["GET", "POST"])
@login_required
def update_user(id_user):
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        user = User.query.get(id_user)
        form = UpdateUser()
        if form.validate_on_submit():
            id_user = int(request.form.get("id_user"))
            user = User.query.get(id_user)
            cinema_check = Cinema.query.filter_by(
                phone_number=form.phone_number.data
            ).first()
            if cinema_check is not None and cinema_check.id != cinema.id:
                return redirect(url_for("update_user", id_user=id_user))
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
            return redirect(url_for("user_manager"))
        return render_template(
            "update_user.html",
            user=user,
            form=form,
            title="Cập nhật thông tin tài khoản",
        )


@app.route("/manager/cinema")
@login_required
def manager_cinema():
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        cinemas = Cinema.query.all()
        return render_template(
            "manager_cinema.html", cinemas=cinemas, title="Quản lý rạp chiếu phim"
        )


@app.route("/manager/cinema/create", methods=["GET", "POST"])
@login_required
def create_cinema():
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        form = CreateCinemaForm()
        if form.validate_on_submit():
            name = form.name.data
            address = form.address.data
            hotline = form.hotline.data
            geomCinema = "Point(" + form.lng.data + " " + form.lat.data + ")"
            new_cinema = Cinema(
                name=name,
                address=address,
                hotline=hotline,
                geom=func.ST_GeomFromText(geomCinema, 4326),
            )

            db.session.add(new_cinema)
            db.session.commit()
            flash("Thêm rạp chiếu phim mới thành công!")
            return redirect(url_for("manager_cinema"))
        return render_template(
            "create_cinema.html", form=form, title="Tạo rạp chiếu phim mới"
        )


@app.route("/api/cinema/all")
@login_required
def read_cinema_all():
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        cinemas = db.session.query(
            Cinema.id,
            Cinema.name,
            Cinema.address,
            Cinema.hotline,
            func.ST_AsGeoJSON(Cinema.geom).label("geometry"),
        ).all()
        cinemasFeatures = []
        for cinema in cinemas:
            properties_temp = {
                "id": cinema.id,
                "name": cinema.name,
                "address": cinema.address,
            }
            geometry_temp = json.loads(cinema.geometry)
            cinema_temp = {
                "type": "Feature",
                "properties": properties_temp,
                "geometry": geometry_temp,
            }
            cinemasFeatures.append(cinema_temp)
        return jsonify({"features": cinemasFeatures})


@app.route("/manager/cinema/all")
def view_cinema_all():
    return render_template("view_cinema_all.html", title="Xem vị trí các rạp")


@app.route("/manager/cinema/update/<int:id_cinema>", methods=["GET", "POST"])
@login_required
def update_cinema(id_cinema):
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        form = UpdateCinemaForm()
        if form.validate_on_submit():
            id_cinema = int(request.form.get("id_cinema"))
            cinema = Cinema.query.get(id_cinema)
            cinema_check = Cinema.query.filter_by(hotline=form.hotline.data).first()
            if cinema_check is not None and cinema_check.id != cinema.id:
                flash("Invalid username or password")
                return redirect(url_for("update_cinema", id_cinema=id_cinema))

            new_name = form.name.data
            new_address = form.address.data
            new_hotline = form.hotline.data
            geomCinema = "Point(" + form.lng.data + " " + form.lat.data + ")"
            new_geom = func.ST_GeomFromText(geomCinema, 4326)
            cinema.name = new_name
            cinema.address = new_address
            cinema.hotline = new_hotline
            cinema.geom = new_geom
            db.session.commit()
            flash("Cập nhật thông tin rạp thành công!")
            return redirect(url_for("view_cinema_all"))

        return render_template(
            "update_cinema.html",
            id_cinema=id_cinema,
            form=form,
            title="Cập nhật thông tin rạp chiếu phim",
        )


@app.route("/manager/cinema/delete/<int:id_cinema>")
@login_required
def delete_cinema(id_cinema):
    id_user = current_user.get_id()
    user = User.query.get(id_user)
    if user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        cinema = Cinema.query.get(id_cinema)
        db.session.delete(cinema)
        db.session.commit()
        flash("Xóa vị trí rạp " + cinema.name + "thành công!")
        return redirect(url_for("manager_cinema"))

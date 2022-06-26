from app import app
from app.models import *
from app import form
from app.form import *
from flask import request, render_template, redirect, flash, url_for, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
import json
from sqlalchemy import or_


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
        flash("Tạo tài khoản thành công! Đăng nhập ngay")
        return redirect(url_for("login"))
    return render_template("sign_up.html", form=form, title="Đăng kí tài khoản")


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
def manager_user():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        users = User.query.all()
        return render_template(
            "manager_user.html", users=users, title="Quản lý tài khoản"
        )


@app.route("/manager/user/delete/<int:id_user>")
def delete_user(id_user):
    user = User.query.get(id_user)
    db.session.delete(user)
    db.session.commit()
    flash("Xóa tài khoản thành công")
    return redirect(url_for("manager_user"))


@app.route("/manager/user/update/<int:id_user>", methods=["GET", "POST"])
@login_required
def update_user(id_user):
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        user = User.query.get(id_user)
        form = UpdateUser()
        if form.validate_on_submit():
            id_user = int(request.form.get("id_user"))
            user = User.query.get(id_user)
            user_check = user.query.filter_by(
                phone_number=form.phone_number.data
            ).first()
            # Kiểm tra số điện thoại cập nhật đã xử dụng chưa
            if user_check is not None and user_check.phone_number != user.phone_number:
                flash("Số điện thoại đã có người sử dụng. Vui lòng dùng số khác!")
                return redirect(url_for("update_user", id_user=id_user))
            user.fullname = form.fullname.data
            user.phone_number = form.phone_number.data
            user.dob = form.dob.data
            user.gender = form.gender.data
            if form.is_admin.data == "True":
                new_is_admin = True
            else:
                new_is_admin = False
            user.is_admin = new_is_admin
            db.session.commit()
            flash("Cập nhật thông tin tài khoản thành công !")
            return redirect(url_for("manager_user"))
        return render_template(
            "update_user.html",
            user=user,
            form=form,
            title="Cập nhật thông tin tài khoản",
        )


@app.route("/manager/cinema")
@login_required
def manager_cinema():
    if current_user.is_admin == False:
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
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        form = CreateCinemaForm()
        if form.validate_on_submit():
            name = form.name.data
            address = form.address.data
            hotline = form.hotline.data
            # lấy gtri lat long và gán vào biến geoCinema dưới dạng điểm
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
            "create_cinema.html", form=form, title="Thêm rạp chiếu phim mới"
        )


@app.route("/api/cinema/all")
@login_required
def read_cinema_all():
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
            "hotline": cinema.hotline,
        }
        geometry_temp = json.loads(cinema.geometry)
        cinema_temp = {
            "type": "Feature",
            "properties": properties_temp,
            "geometry": geometry_temp,
        }
        cinemasFeatures.append(cinema_temp)
    return jsonify({"features": cinemasFeatures})


@app.route("/cinema/maps")
def view_cinema_maps():
    return render_template("view_cinema_maps.html", title="Xem vị trí các rạp")


@app.route("/manager/cinema/update/<int:id_cinema>", methods=["GET", "POST"])
@login_required
def update_cinema(id_cinema):
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        form = UpdateCinemaForm()
        if form.validate_on_submit():
            id_cinema = int(request.form.get("id_cinema"))
            cinema = Cinema.query.get(id_cinema)
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
            return redirect(url_for("view_cinema_maps"))

        return render_template(
            "update_cinema.html",
            id_cinema=id_cinema,
            form=form,
            title="Cập nhật thông tin rạp chiếu phim",
        )


@app.route("/manager/cinema/delete/<int:id_cinema>")
@login_required
def delete_cinema(id_cinema):
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        cinema = Cinema.query.get(id_cinema)
        db.session.delete(cinema)
        db.session.commit()
        flash("Xóa vị trí rạp " + cinema.name + "thành công!")
        return redirect(url_for("manager_cinema"))


@app.route("/manager/ticket")
@login_required
def manager_ticket():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        tickets = Ticket.query.all()
        return render_template(
            "manager_ticket.html",
            tickets=tickets,
            title="Quản lý vé ",
        )


@app.route("/manager/ticket/create/movie")
@login_required
def choose_movie_create_ticket():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        movies = Movie.query.all()
        return render_template(
            "choose_movie_create_ticket.html", movies=movies, title="Chọn phim cho vé"
        )


@app.route("/manager/ticket/create/<int:id_movie>")
@login_required
def create_ticket(id_movie):
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        movie = Movie.query.get(id_movie)
        movie_showtimes = movie.movie_showtimes
        users = User.query.all()
        cinemas = Cinema.query.all()
        return render_template(
            "create_ticket.html",
            movie_showtimes=movie_showtimes,
            users=users,
            cinemas=cinemas,
            id_movie=id_movie,
            title="Tạo vé xem phim mới",
        )


@app.route("/manager/ticket/create/success/<int:id_movie>", methods=["POST"])
def create_ticket_success(id_movie):
    id_movie_showtime = request.form.get("id_movie_showtime")
    ticket_number = int(request.form.get("ticket_number"))
    movie_showtime = Movie_showtime.query.get(id_movie_showtime)
    seats = movie_showtime.seats
    if ticket_number > int(movie_showtime.seats):
        flash("Vé chỉ còn" + movie_showtime.seats + "vé")
        return redirect(url_for("create_movie_showtime", id_movie=id_movie))
    else:
        id_user = request.form.get("id_user")
        id_cinema = request.form.get("id_cinema")
        price = ticket_number * 50000
        new_seats = seats - ticket_number
        movie_showtime.seats = new_seats
        new_ticket = Ticket(
            price=price,
            user_id=id_user,
            cinema_id=id_cinema,
            movie_id=id_movie,
            movie_showtime_id=id_movie_showtime,
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash("Tạo mới vé xem phim thành công")
        return redirect(url_for("manager_ticket"))


@app.route("/manager/ticket/update/movie/ticket_<int:id_ticket>")
@login_required
def choose_movie_update_ticket(id_ticket):
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        movies = Movie.query.all()
        return render_template(
            "choose_movie_update_ticket.html",
            movies=movies,
            id_ticket=id_ticket,
            title="Cập nhật thông tin vé",
        )


@app.route("/manager/ticket/update/ticket_<int:id_ticket>/movie_<int:id_movie>")
@login_required
def update_ticket(id_ticket, id_movie):
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        movie = Movie.query.get(id_movie)
        movie_showtimes = movie.movie_showtimes
        users = User.query.all()
        cinemas = Cinema.query.all()
        return render_template(
            "update_ticket.html",
            id_movie=id_movie,
            id_ticket=id_ticket,
            movie_showtimes=movie_showtimes,
            users=users,
            cinemas=cinemas,
            title="Cập nhật vé xem phim",
        )


@app.route(
    "/manager/ticket/update/success/ticket_<int:id_ticket>/movie_<int:id_movie>",
    methods=["POST"],
)
def update_ticket_success(id_ticket, id_movie):
    id_movie_showtime = request.form.get("id_movie_showtime")
    ticket_number = int(request.form.get("ticket_number"))
    movie_showtime = Movie_showtime.query.get(id_movie_showtime)
    seats = movie_showtime.seats
    if ticket_number > int(movie_showtime.seats):
        flash("Vé chỉ còn" + movie_showtime.seats + "vé")
        return redirect(
            url_for("update_ticket_success", id_ticket=id_ticket, id_movie=id_movie)
        )
    else:
        id_user = request.form.get("id_user")
        id_cinema = request.form.get("id_cinema")
        price = ticket_number * 50000
        new_seats = seats - ticket_number
        movie_showtime.seats = new_seats
        new_ticket = Ticket(
            price=price,
            user_id=id_user,
            cinema_id=id_cinema,
            movie_id=id_movie,
            movie_showtime_id=id_movie_showtime,
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash("Cập nhật vé xem phim")
        return redirect(url_for("manager_ticket"))


@app.route("/manager/ticket/delete/<int:id_ticket>")
@login_required
def delete_ticket(id_ticket):
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        ticket = Ticket.query.get(id_ticket)
        movie_showtime = ticket.movie_showtimes
        seats = movie_showtime.seats
        ticket_number = int(ticket.price) / 50000
        movie_showtime.seats = seats + ticket_number
        db.session.delete(ticket)
        db.session.commit()
        flash("Xóa vé xem phim thành công!")
        return redirect(url_for("manager_ticket"))


@app.route("/manager/user/search")
def search_user():
    search_data = request.args.get("search_data")
    print(search_data)
    users = User.query.all()
    user_searchs = []
    for user in users:
        if user.fullname.find(search_data) != -1 or user.email.find(search_data) != -1:
            user_searchs.append(user)
    if len(user_searchs) >= 1:
        return render_template(
            "manager_user.html", users=user_searchs, title="Quản lý tài khoản"
        )
    else:
        flash("Không tìm thấy giá trị nhập")
        return redirect(url_for("manager_user"))


@app.route("/manager/cinema/search")
def search_cinema():
    search_data = request.args.get("search_data")
    cinemas = Cinema.query.all()
    cinema_searchs = []
    for cinema in cinemas:
        if (
            cinema.name.find(search_data) != -1
            or cinema.address.find(search_data) != -1
        ):
            cinema_searchs.append(cinema)
    if len(cinema_searchs) >= 1:
        return render_template(
            "manager_cinema.html", cinemas=cinema_searchs, title="Quản lý tài khoản"
        )
    else:
        flash("Không tìm thấy giá trị nhập")
        return redirect(url_for("manager_cinema"))


# @app.route("/manager/ticket/search")
# def search_ticket():
#     search_data = request.args.get("search_data")
#     tickets = Ticket.query.all()
#     ticket_searchs = []
#     for ticket in tickets:
#         email_user = ticket.users.email
#         movie_name = ticket.movies.name
#         if email_user.find(search_data) != -1 or movie_name.find(search_data) != -1:
#             ticket_searchs.append(ticket)
#     if len(ticket_searchs) >= 1:
#         return render_template(
#             "manager_ticket.html", tickets=ticket_searchs, title="Quản lý tài khoản"
#         )
#     else:
#         flash("Không tìm thấy giá trị nhập")
#         return redirect(url_for("manager_ticket"))


# ---------Toàn---------
# ---------- Add new movie ----------------


@app.route("/addmovie_s1")
@login_required
def addmovie_s1():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        return render_template("addmovie_s1.html")


@app.route("/addmovie_s2", methods=["POST"])
def addmovie_s2():
    """add new movie"""

    # Get form information.
    name = request.form.get("name")
    img = request.form.get("img")
    describe = request.form.get("describe")
    director = request.form.get("director")
    actor = request.form.get("actor")
    genre = request.form.get("genre")
    running_time = request.form.get("running_time")
    release_date = request.form.get("release_date")
    language = request.form.get("language")
    rated = request.form.get("rated")
    student = Movie(
        name=name,
        img=img,
        describe=describe,
        director=director,
        actor=actor,
        genre=genre,
        running_time=running_time,
        release_date=release_date,
        language=language,
        rated=rated,
    )
    db.session.add(student)
    db.session.commit()
    return render_template("index.html")


# ---------- show new movie ----------------


@app.route("/show_movie")
@login_required
def show_movie():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        movies = Movie.query.all()
        return render_template("show_movie.html", movies=movies)


# ---------- delete new movie ----------------


@app.route("/delete_movie_resul/<int:movie_ids>")
def delete_movie_resul(movie_ids):

    movie = Movie.query.get(movie_ids)
    db.session.delete(movie)
    db.session.commit()
    return render_template("index.html")


# ---------- update new movie ----------------


@app.route("/update_movie_s2/<int:movie_id>")
def update_movie_s2(movie_id):
    movieid = Movie.query.filter(Movie.id == movie_id).all()
    return render_template("update_movie_s2.html", movieid=movieid)


@app.route("/update_movie_resul", methods=["POST", "GET"])
def update_movie_resul():
    movie_id = int(request.form.get("movie_id"))
    name = request.form.get("name")
    img = request.form.get("img")
    describe = request.form.get("describe")
    director = request.form.get("director")
    actor = request.form.get("actor")
    genre = request.form.get("genre")
    running_time = request.form.get("running_time")
    release_date = request.form.get("release_date")
    language = request.form.get("language")
    rated = request.form.get("rated")
    movie = Movie.query.get(movie_id)
    movie.name = name
    movie.img = img
    movie.describe = describe
    movie.director = director
    movie.actor = actor
    movie.genre = genre
    movie.running_time = running_time
    movie.release_date = release_date
    movie.language = language
    movie.rated = rated
    db.session.commit()
    return render_template("index.html")


# ---------- find movie  ----------------


@app.route("/find_movie_s1")
@login_required
def find_movie_s1():
    return render_template("find_movie.html")


@app.route("/find_movie_resul", methods=["POST"])
def find_movie_resul():
    name = request.form.get("fullname")
    # nếu user nhập vào dl vào text
    if name is not None:
        movies = Movie.query.filter(or_(Movie.name == name, Movie.genre == name)).all()
    return render_template("show_movie.html", movies=movies)


# ---------- add movie showtime  ----------------


@app.route("/add_movie_showtime_s1")
@login_required
def add_movie_showtime_s1():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        movies = Movie.query.all()
        return render_template("add_movie_showtime_s1.html", movies=movies)


@app.route("/add_movie_showtime_s2/<int:movie_id>")
def add_movie_showtime_s2(movie_id):
    """add new movie showtime form"""

    movie = Movie.query.get(movie_id)
    return render_template("add_movie_showtime_s2.html", movie=movie)


@app.route("/add_movie_showtime_resul", methods=["POST", "GET"])
def add_movie_showtime_resul():
    """commit add new movie showtime"""

    # Get form information.
    movie_id = int(request.form.get("movie_id"))
    screening_date = request.form.get("screening_date")
    time_start = request.form.get("time_start")
    seats = request.form.get("seats")
    movie_showtime = Movie_showtime(
        movie_id=movie_id,
        screening_date=screening_date,
        time_start=time_start,
        seats=seats,
    )
    db.session.add(movie_showtime)
    db.session.commit()
    return render_template("index.html")


# ---------- Delete movie showtime  ----------------


@app.route("/show_movie_showtime")
@login_required
def show_movie_showtime():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        movie_showtimes = Movie_showtime.query.all()
        return render_template(
            "show_movie_showtime.html", movie_showtimes=movie_showtimes
        )


@app.route("/delete_movie_showtime_resul<int:movie_showtime_id>")
def delete_movie_showtime_resul(movie_showtime_id):

    movie_showtime = Movie_showtime.query.get(movie_showtime_id)
    db.session.delete(movie_showtime)
    db.session.commit()
    return render_template("index.html")


# ---------- update movie showtime  ----------------


@app.route("/update_movie_showtime_s2/<int:movie_showtime_id>")
def update_movie_showtime_s2(movie_showtime_id):
    """add new daily flight form"""
    movie_showtimes = Movie_showtime.query.filter(
        Movie_showtime.id == movie_showtime_id
    ).all()
    return render_template(
        "update_movie_showtime_s2.html", movie_showtimes=movie_showtimes
    )


@app.route("/update_movie_showtime_resul", methods=["POST", "GET"])
def update_movie_showtime_resul():

    movie_showtime_id = int(request.form.get("movie_showtime_id"))
    screening_date = request.form.get("screening_date")
    time_start = request.form.get("time_start")
    seats = request.form.get("seats")
    movie_id = int(request.form.get("movie_id"))
    movie_showtime = Movie_showtime.query.get(movie_showtime_id)
    movie_showtime.movie_id = movie_id
    movie_showtime.screening_date = screening_date
    movie_showtime.time_start = time_start
    movie_showtime.seats = seats
    db.session.commit()
    return render_template("index.html")


# ----------list all Movie_showtime  ----------------


@app.route("/search_movie_showtimea_s1")
@login_required
def search_movie_showtimea_s1():
    """show all Movie"""
    movies = Movie.query.all()
    return render_template("search_movie_showtime_s1.html", movies=movies)


@app.route("/search_movie_showtimea_s2/<int:movie_id>")
def search_movie_showtimea_s2(movie_id):
    """show all student"""
    movie = Movie.query.get(movie_id)
    movie_showtimes = Movie_showtime.query.filter_by(movie_id=movie_id).all()
    return render_template(
        "search_movie_showtime_s2.html", movie=movie, movie_showtimes=movie_showtimes
    )


# ---------- find movie showtime  ----------------


@app.route("/find_movie_showtime_s1")
@login_required
def find_movie_showtime_s1():
    return render_template("find_movie_showtime_s1.html")


@app.route("/find_movie_showtime_resul", methods=["POST"])
def find_movie_showtime_resul():
    name = request.form.get("fullname")
    if name is not None:
        movie_showtimes = Movie_showtime.query.filter(
            or_(Movie_showtime.time_start == name, Movie_showtime.seats == name)
        ).all()
    return render_template("show_movie_showtime.html", movie_showtimes=movie_showtimes)


@app.route("/api/cinema/list")
def read_cinema_list():
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
            "hotline": cinema.hotline,
        }
        geometry_temp = json.loads(cinema.geometry)
        cinema_temp = {
            "type": "Feature",
            "properties": properties_temp,
            "geometry": geometry_temp,
        }
        cinemasFeatures.append(cinema_temp)
    return jsonify({"features": cinemasFeatures})


@app.route("/api/cinema/view")
def api_ciema_view():
    return render_template("geodata.html")


# ---------Việt---------
@app.route("/manager")
@login_required
def manager():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        return render_template("manager.html")


@app.route("/manager/movie")
@login_required
def manager_movie():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        return render_template("manager_movie.html")


@app.route("/manager/movie_showtime")
@login_required
def manager_movie_showtime():
    if current_user.is_admin == False:
        flash("Bạn không có quyền truy cập vào trang web này!")
        return redirect(url_for("index"))
    else:
        return render_template("manager_movie_showtime.html")

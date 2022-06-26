from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    RadioField,
    DateField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
    EqualTo,
)
from app.models import User, Cinema


class SignUpUser(FlaskForm):
    fullname = StringField("Họ tên", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_number = StringField(
        "Số điện thoại",
        validators=[
            DataRequired(),
            Length(min=10, max=10, message=("Số điện thoại bạn nhập không tồn tại!")),
        ],
    )
    dob = DateField("Ngày sinh", validators=[DataRequired()])
    gender = RadioField(
        "Giới tính",
        choices=["Nam", "Nữ", "Khác"],
        validators=[DataRequired()],
    )

    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(),
            Length(min=6, message=("Mật khẩu quá ngắn! Nhập tối thiểu 6 kí tự")),
        ],
    )
    rePassword = PasswordField(
        "Nhập lại mật khẩu",
        validators=[
            DataRequired(),
            EqualTo("password", message="Mật khẩu không trùng!"),
        ],
    )
    submit = SubmitField("Đăng ký")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("Email đã được xử dụng! Hãy sử dụng email khác.")

    def validate_phone(self, phone_number):
        phone_number = User.query.filter_by(phone_number=phone_number.data).first()
        if phone_number is not None:
            raise ValidationError(
                "Số điện thoại đã được xử dụng! Hãy sử dụng Số điện thoại khác."
            )


class UpdateUser(FlaskForm):
    fullname = StringField("Họ tên", validators=[DataRequired()])
    phone_number = StringField(
        "Số điện thoại",
        validators=[
            DataRequired(),
            Length(min=10, max=10, message=("Số điện thoại bạn nhập không tồn tại.")),
        ],
    )
    dob = DateField("Ngày sinh", validators=[DataRequired()])
    gender = RadioField(
        "Giới tính",
        choices=["Nam", "Nữ", "Khác"],
        validators=[DataRequired()],
    )
    is_admin = RadioField("Quản trị viên", choices=["True", "False"])
    submit = SubmitField("Xong")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Mật khẩu", validators=[DataRequired()])
    remember_me = BooleanField("Nhớ tài khoản")
    submit = SubmitField("Đăng nhập")


class CreateCinemaForm(FlaskForm):
    name = StringField("Tên rạp chiếu phim", validators=[DataRequired()])
    address = StringField("Địa chỉ", validators=[DataRequired()])
    hotline = StringField("Hotline", validators=[DataRequired()])
    lng = StringField("Kinh độ", validators=[DataRequired()])
    lat = StringField("Vĩ độ", validators=[DataRequired()])
    submit = SubmitField("Thêm")


class UpdateCinemaForm(FlaskForm):
    name = StringField("Tên rạp chiếu phim", validators=[DataRequired()])
    address = StringField("Địa chỉ", validators=[DataRequired()])
    hotline = StringField("Hotline", validators=[DataRequired()])
    lng = StringField("Kinh độ", validators=[DataRequired()])
    lat = StringField("Vĩ độ", validators=[DataRequired()])
    submit = SubmitField("Cập nhật")

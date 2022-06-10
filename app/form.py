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
from app.models import User


class SignUpUser(FlaskForm):
    fullname = StringField("Họ tên", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_number = StringField("Số điện thoại", validators=[DataRequired()])
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
            Length(min=6, message=("Your password is too short.")),
        ],
    )
    rePassword = PasswordField(
        "Nhập lại mật khẩu",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Xong")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError(
                "Email has been already used! Please use a different email."
            )

    def validate_phone(self, phone_number):
        phone_number = User.query.filter_by(phone_number=phone_number.data).first()
        if phone_number is not None:
            raise ValidationError(
                "Phone number has been already used! Please use a different phone number."
            )


class SignUpUser(FlaskForm):
    fullname = StringField("Họ tên", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_number = StringField("Số điện thoại", validators=[DataRequired()])
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
            Length(min=6, message=("Your password is too short.")),
        ],
    )
    rePassword = PasswordField(
        "Nhập lại mật khẩu",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Đăng ký")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError(
                "Email has been already used! Please use a different email."
            )

    def validate_phone(self, phone_number):
        phone_number = User.query.filter_by(phone_number=phone_number.data).first()
        if phone_number is not None:
            raise ValidationError(
                "Phone number has been already used! Please use a different phone number."
            )


class UpdateUser(FlaskForm):
    fullname = StringField("Họ tên", validators=[DataRequired()])
    phone_number = StringField("Số điện thoại", validators=[DataRequired()])
    dob = DateField("Ngày sinh", validators=[DataRequired()])
    gender = RadioField(
        "Giới tính",
        choices=["Nam", "Nữ", "Khác"],
        validators=[DataRequired()],
    )
    is_admin = RadioField("Quản trị viên", choices=["True", "False"])
    submit = SubmitField("Xong")

    def validate_phone(self, phone_number):
        phone_number = User.query.filter_by(phone_number=phone_number.data).first()
        if phone_number is not None:
            raise ValidationError(
                "Phone number has been already used! Please use a different phone number."
            )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Mật khẩu", validators=[DataRequired()])
    remember_me = BooleanField("Nhớ tài khoản")
    submit = SubmitField("Đăng nhập")

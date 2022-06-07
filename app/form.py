from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
    EqualTo,
    InputRequired,
)

from models import User


class signUpForm(FlaskForm):
    fullname = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    dob = StringField("DOB", validators=[DataRequired()])
    gender = StringField("Gender", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message=("Your password is too short.")),
        ],
    )
    rePassword = PasswordField(
        "reType Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Sign Up")

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


class loginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")

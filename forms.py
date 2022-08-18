from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, DateField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    user_name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class IngredientForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    category = SelectField('Category', choices=[('fruit', 'fruit'), ('vegetable', 'vegetable')])
    date_expired = DateField('Expiration Date', validators=[DataRequired()])
    submit = SubmitField("Add Ingredient")

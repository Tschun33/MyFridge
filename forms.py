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
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class IngredientForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    category = SelectField('Category', choices=[('Fruit', 'Fruit'), ('Vegetable', 'Vegetable'), ('Dairy', 'Dairy'),
                                                ('Cheese', 'Cheese')])
    date_expired = DateField('Expiration Date')
    submit = SubmitField("Add Ingredient")

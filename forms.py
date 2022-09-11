from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, DateField, DecimalField
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


class FoodForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    quantity = DecimalField("Quantity", validators=[DataRequired()])
    category = SelectField('Category', choices=[('Fruit', 'Fruit'), ('Vegetable', 'Vegetable'), ('Dairy', 'Dairy'),
                                                ('Cheese', 'Cheese'), ('Raw Meat', 'Raw Meat')])
    date_expired = DateField('Expiration Date')
    submit = SubmitField("Add Ingredient")

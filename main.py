from datetime import date
import werkzeug.security
from flask import Flask, render_template, redirect, url_for, flash, jsonify, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from flask import abort
from forms import RegisterForm, LoginForm, FoodForm

app = Flask(__name__)
# for learning purpose only
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# DB Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fridge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(id=user_id).first()

# Models
class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    date_added = db.Column(db.Date, nullable=False)
    date_expired = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    # User has many ingridients
    food = db.relationship('Food', backref='user')
    recipe = db.relaionship('Recipe', backref='user')


class Recipe(UserMixin, db.Model):
    __tablename__= 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ingredient = db.relationship('Ingredient', backref='recipe')


class Ingredient(UserMixin, db.Model):
    __tablename__= 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))


db.create_all()


# Admin only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# for learning purpose only. API-Key should be environment variable
def api_key_provided(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args.get("api-key") != "SecretApiKey":
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_name = form.name.data
        new_username = form.user_name.data
        new_email = form.email.data
        new_password = form.password.data
        if db.session.query(User).filter_by(email=new_email).first():
            flash('You already signed up! Login instead')
            return redirect("login")
        else:
            hashed_password = werkzeug.security.generate_password_hash(new_password, method="pbkdf2:sha256",
                                                                       salt_length=8)
            new_user = User(
                name=new_name,
                user_name=new_username,
                password=hashed_password,
                email=new_email
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user_password = form.password.data
        if not db.session.query(User).filter_by(email=user_email).first():
            flash('This email address is not registered')
        else:
            user = db.session.query(User).filter_by(email=user_email).first()
            if check_password_hash(user.password, user_password):
                login_user(user)
                flash('Login successful')
                return redirect(url_for('home'))
            else:
                error = "Invalid Credentials"
                flash(error)
                return redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add_food():
    form = FoodForm()
    if form.validate_on_submit():
        new_food = Food(
            name=form.name.data,
            quantity=form.quantity.data,
            date_added=date.today(),
            user=current_user,
            date_expired=form.date_expired.data,
            category=form.category.data
        )
        db.session.add(new_food)
        db.session.commit()
        return redirect(url_for("show_fridge"))

    return render_template("add-food.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/fridge")
@login_required
def show_fridge():
    user = current_user
    items = db.session.query(Food).filter_by(user_id=current_user.id).all()
    return render_template("fridge.html", items=items)


# RESTful Routes
@app.route("/all")
def get_all():
    if request.args.get("api-key") == "SecretApiKey":
        ingredients = db.session.query(Food).all()
        return jsonify(ingredients=[ingredient.to_dict() for ingredient in ingredients])
    else:
        return jsonify(response={"error": "Not allowed"})


@app.route("/by_user/<user_id>", methods=["GET"])
@api_key_provided
def get_by_user(user_id):
    ingredients = db.session.query(Food).filter_by(user_id=user_id).all()
    return jsonify(ingredients=[ingredient.to_dict() for ingredient in ingredients])


@app.route("/add_to_user/<user_id>", methods=["POST"])
@api_key_provided
def add_to_user(user_id):
    new_food = Food(
        name=request.args.get("name"),
        date_added=date.today(),
        user=user_id,
        date_expired=request.args.get("date_expired"),
        category=request.args.get("category")
    )
    db.session.add(new_food)
    db.session.commit()
    return jsonify(response={"success:": "Item added successfully"})


@app.route("/update_date_expired/<ingredient_id>", methods=["PATCH"])
@api_key_provided
def update_ingredient(ingredient_id):
    ingredient_to_update = db.session.query(Food).filter_by(ingredient_id).first()
    new_date_expired = request.args.get("date_expired")
    ingredient_to_update.date_expired = new_date_expired
    db.session.commit()
    return jsonify(response={"success": "Item successfully updated"})


# Runs the application
if __name__ == "__main__":
    app.run(debug=True)

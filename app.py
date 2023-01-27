import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length, Email
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from getpass import getpass
import os

app = Flask(__name__)
Bootstrap(app)
app.secret_key = "orewagundam"
is_user_logged = False
shopping_list = []


# CONNECT WITH DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bakulgundam.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# DATABASE STRUCTURE
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(32), nullable=False)
    model = db.Column(db.String(32), nullable=False)
    brand = db.Column(db.String(8), nullable=False)
    grade = db.Column(db.String(16), nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(512), nullable=True)
    img1 = db.Column(db.String(128), nullable=True)
    img2 = db.Column(db.String(128), nullable=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(32), nullable=False)
    alamat = db.Column(db.String(32), nullable=False)
    kodezip = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)


class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), nullable=False, unique=True)


# FORMS
class LogForm(FlaskForm):
    email = StringField(label="email", validators=[DataRequired(),
                                                   Email(message="invalid email address")])
    password = PasswordField(label="password", validators=[DataRequired(),
                                                           Length(min=8, message="password too short")])
    submit = SubmitField(label="log in")


class RegisterForm(FlaskForm):
    email = StringField(label="email", validators=[DataRequired(),
                                                   Email(message="invalid email address")])
    password = PasswordField(label="password", validators=[InputRequired(),
                                                           EqualTo("password2", message="passwords must match"),
                                                           Length(min=8, message="password too short")])
    password2 = PasswordField(label="repeat password")
    nama = StringField(label="nama lengkap", validators=[DataRequired()])
    alamat = StringField(label="alamat", validators=[DataRequired()])
    kodezip = StringField(label="kodezip", validators=[DataRequired()])
    submit = SubmitField(label="register")


class NewsletterForm(FlaskForm):
    email = StringField(label="email")
    sign_in = SubmitField(label="sign up")


class SearchForm(FlaskForm):
    item = StringField()
    search = SubmitField(label="search")


class LogoutForm(FlaskForm):
    logout = SubmitField(label="log out")


class AddForm(FlaskForm):
    add = SubmitField(label="add to shopping cart")

with app.app_context():
    db.create_all()

def add_to_newsletter(email):
    if not email == "":
        try:
            db.session.add(Newsletter(email=email))
            db.session.commit()
        except:
            pass
        finally:
            pass


@app.route("/", methods=["GET", "POST"])
def homepage():
    global is_user_logged
    global shopping_list

    newsletter = NewsletterForm()
    logout = LogoutForm()

    if newsletter.validate_on_submit() and newsletter.sign_in.data:
        add_to_newsletter(newsletter.email.data)

    if logout.is_submitted() and not newsletter.sign_in.data:
        is_user_logged = False
        shopping_list = []

    return render_template("index.html",
                           current_year=datetime.now().year,
                           newsletter=newsletter,
                           logout=logout,
                           is_user_logged=is_user_logged)


@app.route("/shop", methods=["GET", "POST"])
def shop():
    items = db.session.query(Item).all()
    temp_items = []

    newsletter = NewsletterForm()
    logout = LogoutForm()
    search = SearchForm()

    if newsletter.validate_on_submit() and newsletter.sign_in.data:
        add_to_newsletter(newsletter.email.data)

    if search.validate_on_submit() and search.search.data:
        for item in items:
            if item.model.lower().find(search.item.data.lower()) != -1:
                temp_items.append(item)
            elif item.brand.lower().find(search.item.data.lower()) != -1:
                temp_items.append(item)

        items = temp_items.copy()
        temp_items = []

    brand = request.args.get("brand")
    grade = request.args.get("grade")
    sort = request.args.get("sort_by")

    if brand:
        for item in items:
            if item.brand == brand:
                temp_items.append(item)

        items = temp_items.copy()
        temp_items = []

    if grade:
        for item in items:
            if item.grade == grade:
                temp_items.append(item)

        items = temp_items.copy()
        temp_items = []

    if sort == "harga":
        items.sort(key=lambda x: x.harga)

    elif sort == "model":
        items.sort(key=lambda x: x.model)

    return render_template("shop.html",
                           current_year=datetime.now().year,
                           all_items=items,
                           brand=brand,
                           grade=grade,
                           sort=sort,
                           newsletter=newsletter,
                           logout=logout,
                           search=search,
                           is_user_logged=is_user_logged)


@app.route("/shop/<int:item_id>", methods=["GET", "POST"])
def item(item_id):
    global size

    item = Item.query.filter_by(id=item_id).first()

    newsletter = NewsletterForm()
    logout = LogoutForm()
    add = AddForm()

    if newsletter.validate_on_submit() and newsletter.sign_in.data:
        add_to_newsletter(newsletter.email.data)

    if add.validate_on_submit():
        flash("Berhasil memasukkan ke keranjang", "info")
        shopping_list.append(item)

    return render_template("item.html",
                           current_year=datetime.now().year,
                           item=item,
                           newsletter=newsletter,
                           logout=logout,
                           add=add,
                           is_user_logged=is_user_logged,
                           shopping_list=shopping_list)


@app.route("/about", methods=["GET", "POST"])
def about():
    newsletter = NewsletterForm()
    logout = LogoutForm()

    if newsletter.validate_on_submit() and newsletter.sign_in.data:
        add_to_newsletter(newsletter.email.data)

    return render_template("about.html",
                           current_year=datetime.now().year,
                           newsletter=newsletter,
                           logout=logout,
                           is_user_logged=is_user_logged)


@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    global is_user_logged

    form = LogForm()
    newsletter = NewsletterForm()

    if newsletter.validate_on_submit() and newsletter.sign_in.data:
        add_to_newsletter(newsletter.email.data)

    elif form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.password, form.password.data):
                flash("Anda telah berhasil login, selamat khilaf", "info")
                is_user_logged = True
                return redirect(url_for("homepage"))
            else:
                flash("Password salah", "info")
        except AttributeError:
            flash("Tidak ada akun dengan email ini, buatlah akun baru", "info")
            return redirect(url_for("register"))
        finally:
            pass

    return render_template("log_in.html",
                           current_year=datetime.now().year,
                           form=form,
                           newsletter=newsletter)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    newsletter = NewsletterForm()

    if newsletter.validate_on_submit() and newsletter.sign_in.data:
        add_to_newsletter(newsletter.email.data)

    elif form.validate_on_submit():
        try:
            db.session.add(User(nama=form.nama.data,
                                alamat=form.alamat.data,
                                kodezip=form.kodezip.data,
                                email=form.email.data,
                                password=generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)))

            db.session.commit()

            flash("Akun telah berhasil dibuat, log in", "info")
            return redirect(url_for("log_in"))
        except sqlalchemy.exc.IntegrityError:
            flash("Akun sudah dibuat, silahkan log in", "info")
            return redirect(url_for("log_in"))
        finally:
            pass

    return render_template("register.html",
                           current_year=datetime.now().year,
                           form=form,
                           newsletter=newsletter)


@app.route("/shopping-cart", methods=["GET", "POST"])
def cart():
    newsletter = NewsletterForm()
    logout = LogoutForm()

    harga = 0

    if newsletter.validate_on_submit() and newsletter.sign_in.data:
        add_to_newsletter(newsletter.email.data)

    for item in shopping_list:
        harga += item.harga

    return render_template("shopping-cart.html",
                           current_year=datetime.now().year,
                           newsletter=newsletter,
                           logout=logout,
                           is_user_logged=is_user_logged,
                           shopping_list=shopping_list,
                           harga=harga)


if __name__ == "__main__":
    app.run(debug=True)

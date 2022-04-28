import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm
from  admin.admin import admin

# configuration
from werkzeug.utils import redirect

from FDataBase import FDataBase
from UserLogin import UserLogin

DATABASE = '/tmp/Flask.db'
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', '../.env')
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, '../Flask.db')))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Log in to access restricted pages"
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Helper function for creating database tables"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Connecting to the database if it is not already established"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    """Close the connection to the database if it was established"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


dbase = None


@app.before_request
def before_request():
    """Establishing a database connection before executing a query"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.route('/')
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route('/add_post', methods=['POST', 'GET'])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(
                request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Error adding article', category='error')
            else:
                flash('Article added successfully', category='success')
        else:
            flash('Error adding article', category='error')
    return render_template('add_post.html', menu=dbase.getMenu(), title='Adding an article')


@app.route('/post/<alias>')
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route("/login", methods=["POST", "GET"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    form.psw.flags.__delattr__('maxlength')
    form.psw.flags.__delattr__('minlength')
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Invalid username/password pair", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Authorization", form=form)

    # if request.method == 'POST':
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['psw'], request.form['psw']):
    #         userlogin = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         login_user(userlogin, remember=rm)
    #         return redirect(request.args.get("next") or url_for("profile"))
    #
    #     flash('Invalid username/password pair', 'error')
    #
    # return render_template('login.html', menu=dbase.getMenu(), title='Authorization')


@app.route("/register", methods=["POST", "GET"])
def register():

    form = RegisterForm()
    form.psw.flags.__delattr__('maxlength')
    form.psw.flags.__delattr__('minlength')
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
           flash("You have successfully registered", "success")
           return redirect(url_for('login'))
        else:
            flash("Error adding user to DB", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Registration", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are logged out", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Profile")


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash('Avatar update error', 'error')
                flash('Avatar updated', 'success')
            except FileNotFoundError as e:
                flash('File read error', "error")
        else:
            flash('Avatar update error', 'error')

    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)

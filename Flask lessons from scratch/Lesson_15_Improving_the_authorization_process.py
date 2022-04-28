import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# configuration
from werkzeug.utils import redirect

from FDataBase import FDataBase
from UserLogin import UserLogin

DATABASE = '/tmp/Flask.db'
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', '../.env')

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, '../Flask.db')))

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


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash('Invalid username/password pair', 'error')

    return render_template('login.html', menu=dbase.getMenu(), title='Authorization')


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("You have successfully registered", "success")
                return redirect(url_for('login'))
            else:
                flash("Error adding user to DB", "error")
        else:
            flash("Fields filled out incorrectly", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Registration")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are logged out", "success" )
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"""<p><a href="{url_for('logout')}">Sign out</a>
            <p>user info: {current_user.get_id()}"""

if __name__ == '__main__':
    app.run(debug=True)

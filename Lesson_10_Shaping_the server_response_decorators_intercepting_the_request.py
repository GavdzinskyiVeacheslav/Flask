from flask import Flask, render_template, make_response, url_for
from werkzeug.utils import redirect

app = Flask(__name__)

menu = [{"title" : "Main", "url" : "/"},
        {"title" : "Add article", "url" : "/add_post"}]

@app.route("/")
def index():
    # res = make_response("<h1>Server error</h1>", 500)
    # return res
    return "<h1>Main Page</h1>", 200, {'Content-Type': 'text/plain'}

@app.errorhandler(404)
def pageNot(error):
    return ("Page not found", 404)

@app.route('/transfer')
def transfer():
    return redirect(url_for('index'), 301)

    """
    img = None
    with app.open_resource(app.root_path + "/static/images/ava.png", mode="rb") as f:
        img = f.read()
    if img is None:
        return "None image"
    res = make_response(img)
    res.headers['Content-Type'] = 'image/png'
    return res
    """

    # content = render_template('index.html', menu=menu, posts=[])
    # res = make_response(content)
    # res.headers['Content-Type'] = 'text/plain'
    # res.headers['Server'] = 'flasksite'
    # return res

@app.before_first_request
def before_first_request():
    print("before_first_request() called")

@app.before_request
def before_request():
    print("before_request() called")

@app.after_request
def after_request(response):
    print("after_request() called")
    return response

@app.teardown_request
def teardown_request(response):
    print("teardown_request() called")
    return response


if __name__ == "__main__":
    app.run(debug=True)
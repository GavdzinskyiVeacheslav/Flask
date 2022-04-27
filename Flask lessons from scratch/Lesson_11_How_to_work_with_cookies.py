from flask import Flask, render_template, make_response, url_for, request
app = Flask(__name__)
menu = [{"title" : "Main", "url" : "/"},
        {"title" : "Add article", "url" : "/add_post"}]

@app.route("/")
def index():
    return "<h1>Main Page</h1>"

@app.route('/login')
def login():
    log = ""
    if request.cookies.get('logged'):
        log = request.cookies.get('logged')

    res = make_response(f'<h1>Authorization form</h1><p>logged: {log}')
    res.set_cookie('logged', 'yes', 30*24*3600)
    return res

@app.route('/logout')
def logout():
    res = make_response('<p>You are no longer authorized!</p>')
    res.set_cookie('logged', "", 0)
    return res

if __name__ == "__main__":
    app.run(debug=True)








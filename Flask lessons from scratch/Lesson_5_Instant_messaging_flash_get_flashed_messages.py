import os
from flask import Flask, render_template, url_for, request, flash

app = Flask(__name__)

menu = [{"name" : "Installation", "url": "install-flask"},
        {"name" : "First application", "url": "first-app"},
        {"name" : "Feedback", "url": "contact" }]

app.secret_key = os.environ.get('SECRET_KEY', '../.env')

@app.route('/')
def index():
    return render_template('index.html', menu = menu)

@app.route("/about")
def about():
    return render_template('about.html', title = "About the site", menu = menu)

@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash("The message has been sent", category='success')
        else:
            flash("Send error", category='error')

    return render_template('contact.html', title = "Feedback", menu = menu)

if __name__ == "__main__":
    app.run(debug=True)
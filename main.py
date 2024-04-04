from flask import Flask, render_template, redirect, url_for, flash

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/projects')
def projects():
    return render_template('index.html', anchor='projects')

@app.route('/skills')
def skills():
    return render_template('index.html', anchor='skills')

@app.route('/about')
def about():
    return render_template('index.html', anchor='about')

@app.route('/contact')
def contact():
    return render_template('index.html', anchor='contact')

if __name__ == "__main__":
    app.run(port=5500, host="0.0.0.0")
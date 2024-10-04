from flask import Flask, render_template, jsonify, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/members")
def members():
    return jsonify({"members": ["Member1", "Member2", "Member3"]})

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, jsonify, redirect, request, url_for
import sqlite3
import bcrypt

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect('registration.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registration_data (name TEXT, email TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return redirect(url_for('login_page'))

@app.route("/login", methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route("/login", methods=['POST'])
def login():
    try:
        data = request.get_json()  
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        conn = sqlite3.connect('registration.db')
        c = conn.cursor()

        c.execute('SELECT * FROM registration_data WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if user is None:
            return jsonify({"error": "User not found"}), 404

        stored_password = user[2]  

        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/signup", methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route("/signup", methods=['POST'])
def signup():
    try:
        data = request.get_json()  # Get JSON data from the request
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('registration.db')
        c = conn.cursor()

        c.execute('INSERT INTO registration_data (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password.decode('utf-8')))
        conn.commit()
        conn.close()

        return jsonify({"message": "Sign up successful! Please log in."}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/home", methods=['GET'])
def home():
    return render_template('home.html')

@app.route("/members", methods=['GET'])
def members():
    return jsonify({"members": ["Member1", "Member2", "Member3"]})

if __name__ == "__main__":
    create_database()  
    app.run(debug=True)

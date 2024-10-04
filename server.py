from flask import Flask, render_template, jsonify, redirect, request, url_for
import sqlite3
import bcrypt
from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
import astropy.units as u
import pandas as pd
import numpy as np
import math
import time


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


@app.route('/visualization')
def visualization():
    name = request.args.get('name')
    dec = request.args.get('dec')
    ra = request.args.get('ra')
    distance = request.args.get('distance')
    host = request.args.get('host')
    star_data = get_star_data(ra , dec , distance)
    return render_template('visualization.html', name=name, dec=dec, ra=ra, distance=distance, host=host ,star_data=jsonify(star_data).get_data(as_text=True))


def get_star_data(ra_center, dec_center, distance_center):
    # Define the center of the sphere (in ICRS coordinates)
    sphere_radius = 25  # Radius in parsecs

    try:
        # Convert distance to float and validate it
        print(1)
        distance_center = float(distance_center)
        print(2)
        ra_center=float(ra_center)
        print(3)
        dec_center=float(dec_center)
        print(4)
        if distance_center <= 0:
            raise ValueError("Distance must be greater than 0.")

        # Check if distance_center is greater than sphere_radius
        if distance_center <= sphere_radius:
            distance_center=sphere_radius+1
            # raise ValueError("Distance must be greater than the sphere radius.")

        # Calculate parallax range
        parallax_center = 1000 / distance_center
        parallax_min = 1000 / (distance_center + sphere_radius)
        parallax_max = 1000 / (distance_center - sphere_radius)

        # Calculate angular radius
        angular_radius = np.degrees(np.arcsin(sphere_radius / distance_center))

        # Construct ADQL query
        query = f"""
        SELECT TOP 5000
            source_id,
            ra,
            dec,
            parallax
        FROM gaiadr3.gaia_source
        WHERE 1=CONTAINS(
            POINT('ICRS', ra, dec),
            CIRCLE('ICRS', {ra_center}, {dec_center}, {angular_radius})
        )
        AND parallax BETWEEN {parallax_min} AND {parallax_max}
        AND parallax_over_error > 5
        """

        # Execute the query
        job = Gaia.launch_job_async(query)
        results = job.get_results()

        # Check if results are empty
        if results is None or len(results) == 0:
            return []

        # Convert results to a pandas DataFrame
        df = results.to_pandas()

        # Filter for valid parallax values
        df = df[df['parallax'] > 0]

        # Calculate distances and relative positions
        center_coord = SkyCoord(ra=ra_center * u.degree, dec=dec_center * u.degree, distance=distance_center * u.pc)
        distances = (1000 / df['parallax'].values) * u.pc
        star_coords = SkyCoord(ra=df['ra'].values * u.degree, dec=df['dec'].values * u.degree, distance=distances)

        # Calculate relative positions
        relative_positions = star_coords.cartesian - center_coord.cartesian

        # Add new columns for relative Cartesian coordinates
        df['x'] = relative_positions.x.value
        df['y'] = relative_positions.y.value
        df['z'] = relative_positions.z.value

        # Calculate additional fields
        df['d_rel'] = np.sqrt(df['x'] ** 2 + df['y'] ** 2 + df['z'] ** 2)
        df['RA_rel'] = np.arctan2(df['y'], df['x'])
        df['Dec_rel'] = np.arcsin(df['z'] / df['d_rel'])

        return df.to_dict(orient='records')

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == "__main__":
    create_database()  
    app.run(debug=True)

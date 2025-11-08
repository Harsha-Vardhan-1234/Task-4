from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# ----------------------------
# ⚙️ Flask App Setup
# ----------------------------
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "mediconnect_secret_key"


# ----------------------------
# 🧩 Database Setup
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect("mediconnect.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )''')

    # HOSPITALS TABLE
    cur.execute('''CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        latitude REAL,
        longitude REAL
    )''')

    # DOCTORS TABLE
    cur.execute('''CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT,
        experience INTEGER,
        hospital_id INTEGER,
        contact TEXT,
        email TEXT,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
    )''')

    conn.commit()
    conn.close()

init_db()


# ----------------------------
# 👤 Register Route
# ----------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "All fields are required."}), 400

    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                    (name, email, hashed_pw))
        conn.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists!"}), 400
    finally:
        conn.close()


# ----------------------------
# 🔐 Login Route
# ----------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user"] = {"id": user["id"], "name": user["name"], "role": user["role"]}
        return jsonify({
            "message": "Login successful!",
            "user": {"id": user["id"], "name": user["name"], "role": user["role"]}
        }), 200
    else:
        return jsonify({"error": "Invalid email or password!"}), 401


# ----------------------------
# 🚪 Logout
# ----------------------------
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200


# ----------------------------
# 🏥 Hospital CRUD
# ----------------------------
@app.route("/api/hospitals", methods=["GET"])
def get_hospitals():
    conn = get_db_connection()
    hospitals = conn.execute("SELECT * FROM hospitals").fetchall()
    conn.close()
    return jsonify([dict(row) for row in hospitals])


@app.route("/api/hospitals", methods=["POST"])
def add_hospital():
    data = request.json
    conn = get_db_connection()
    conn.execute("INSERT INTO hospitals (name, address, latitude, longitude) VALUES (?, ?, ?, ?)",
                 (data["name"], data["address"], data.get("latitude"), data.get("longitude")))
    conn.commit()
    conn.close()
    return jsonify({"message": "Hospital added successfully!"})


@app.route("/api/hospitals/<int:id>", methods=["DELETE"])
def delete_hospital(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM hospitals WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Hospital deleted successfully!"})


# ----------------------------
# 👨‍⚕️ Doctors CRUD
# ----------------------------
@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    conn = get_db_connection()
    doctors = conn.execute("""
        SELECT doctors.*, hospitals.name AS hospital_name
        FROM doctors
        LEFT JOIN hospitals ON doctors.hospital_id = hospitals.id
    """).fetchall()
    conn.close()
    return jsonify([dict(row) for row in doctors])


@app.route("/api/doctors", methods=["POST"])
def add_doctor():
    data = request.json
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO doctors (name, specialization, experience, hospital_id, contact, email)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["name"], data["specialization"], data["experience"],
          data["hospital_id"], data["contact"], data["email"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Doctor added successfully!"})


@app.route("/api/doctors/<int:id>", methods=["DELETE"])
def delete_doctor(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM doctors WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Doctor deleted successfully!"})


# ----------------------------
# 🔍 Search (for index.html)
# ----------------------------
@app.route("/api/search", methods=["GET"])
def search_doctors():
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify([])

    conn = get_db_connection()
    doctors = conn.execute("""
        SELECT 
            doctors.id AS doctor_id,
            doctors.name AS doctor_name,
            doctors.specialization,
            doctors.experience,
            doctors.contact,
            doctors.email,
            hospitals.id AS hospital_id,
            hospitals.name AS hospital_name,
            hospitals.address
        FROM doctors
        JOIN hospitals ON doctors.hospital_id = hospitals.id
        WHERE doctors.specialization LIKE ? 
           OR doctors.name LIKE ? 
           OR hospitals.name LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
    conn.close()

    return jsonify([dict(row) for row in doctors])


# ----------------------------
# 🏠 Homepage
# ----------------------------
@app.route("/")
def home():
    return """
    <html><body style='font-family:sans-serif;text-align:center;margin-top:50px'>
    <h2>🩺 MediConnect Backend Running Successfully!</h2>
    <p>Use endpoints like:</p>
    <ul style='list-style:none'>
    <li><a href='/api/doctors'>/api/doctors</a></li>
    <li><a href='/api/hospitals'>/api/hospitals</a></li>
    <li><a href='/api/search?q=heart'>/api/search?q=heart</a></li>
    </ul>
    </body></html>
    """


# ----------------------------
# 🚀 Run App
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)

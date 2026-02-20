from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import json
import re
from flask_bcrypt import Bcrypt
import os
import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

DB_PATH = "database.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

app = Flask(__name__)
app.secret_key = "supersecretkey"
bcrypt = Bcrypt(app)

# Load ISL mapping
with open("mapping.json", encoding="utf-8") as f:
    char_map = json.load(f)


def get_db():
    return sqlite3.connect("database.db")


# ---------------- PASSWORD VALIDATION ----------------
def validate_password(password):
    if len(password) < 8:
        return "Too short! Minimum 8 characters 😅"

    letters = len(re.findall(r"[A-Za-z]", password))
    numbers = len(re.findall(r"[0-9]", password))
    special = len(re.findall(r"[!@#$%^&*(),.?\":{}|<>]", password))

    if letters < 4:
        return "We need at least 4 letters 🔤"

    if numbers < 3:
        return "Add at least 3 numbers 🔢"

    if special < 1:
        return "Don't forget 1 special character ✨"

    return None


# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("index"))
    return redirect(url_for("login"))


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # validate password
        error = validate_password(password)
        if error:
            flash(error, "error")
            return redirect(url_for("signup"))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pw),
            )

            conn.commit()
            conn.close()

            flash("Account created successfully! 🚀", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            # REAL duplicate username case
            flash("Oops! That username is already taken 🚫", "error")
            return redirect(url_for("signup"))

        except Exception as e:
            # show real hidden error in terminal
            print("DATABASE ERROR:", e)
            flash("Database error occurred. Check terminal.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and bcrypt.check_password_hash(result[0], password):
            session["user"] = username
            return redirect(url_for("index"))

        flash("Hmm... those credentials don't look right 🤔", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- INDEX ----------------
@app.route("/index", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    images = []
    text = ""
    warning = ""

    if "count" not in session:
        session["count"] = 0

    if request.method == "POST":
        text = request.form.get("text_input", "")

        if any(c.isalpha() and c.islower() for c in text):
            warning = "⚠ Please type English letters in ALL CAPS."

        for ch in text:
            if ch in char_map:
                images.append((ch, char_map[ch]))

        if text.strip():
            session["count"] += 1

    return render_template(
        "index.html",
        text=text,
        images=images,
        warning=warning,
        count=session["count"],
        user=session["user"]
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)

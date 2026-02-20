from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import json
import re
from flask_bcrypt import Bcrypt
from collections import Counter

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "supersecretkey"
bcrypt = Bcrypt(app)

DB_PATH = "database.db"


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            input_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Initialize database
init_db()


# ---------------- LOAD CHARACTER MAP ----------------
with open("mapping.json", encoding="utf-8") as f:
    char_map = json.load(f)


# ---------------- PASSWORD VALIDATION ----------------
def validate_password(password):
    if len(password) < 8:
        return "Minimum 8 characters required 😅"

    letters = len(re.findall(r"[A-Za-z]", password))
    numbers = len(re.findall(r"[0-9]", password))
    special = len(re.findall(r"[!@#$%^&*(),.?\":{}|<>]", password))

    if letters < 4:
        return "At least 4 letters required 🔤"

    if numbers < 3:
        return "Add at least 3 numbers 🔢"

    if special < 1:
        return "Include at least 1 special character ✨"

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
        username = request.form["username"].strip()
        password = request.form["password"]

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
            flash("Username already exists 🚫", "error")
            return redirect(url_for("signup"))

        except Exception as e:
            print("DATABASE ERROR:", e)
            flash("Database error occurred.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and bcrypt.check_password_hash(result["password"], password):
            session["user"] = username
            return redirect(url_for("index"))

        flash("Invalid credentials 🤔", "error")
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

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO translations (username, input_text) VALUES (?, ?)",
                (session["user"], text)
            )
            conn.commit()
            conn.close()

    return render_template(
        "index.html",
        text=text,
        images=images,
        warning=warning,
        count=session["count"],
        user=session["user"]
    )


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # ---------------- TOTAL TRANSLATIONS ----------------
    cursor.execute("SELECT COUNT(*) as total FROM translations")
    total = cursor.fetchone()["total"]

    # ---------------- UNIQUE USERS ----------------
    cursor.execute("SELECT COUNT(DISTINCT username) as unique_users FROM translations")
    unique_users = cursor.fetchone()["unique_users"]

    # ---------------- TOP USERS ----------------
    cursor.execute("""
        SELECT username, COUNT(*) as count
        FROM translations
        GROUP BY username
        ORDER BY count DESC
        LIMIT 5
    """)
    top_users_raw = cursor.fetchall()
    top_users = [(row["username"], row["count"]) for row in top_users_raw]

    # ---------------- DAILY TREND ----------------
    cursor.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as count
        FROM translations
        GROUP BY day
        ORDER BY day
    """)
    daily_raw = cursor.fetchall()
    daily_data = [(row["day"], row["count"]) for row in daily_raw]

    # ---------------- CHARACTER FREQUENCY ----------------
    cursor.execute("SELECT input_text FROM translations")
    texts = cursor.fetchall()
    conn.close()

    all_chars = ""

    for row in texts:
        # Keep original characters (no forced uppercase)
        all_chars += row["input_text"]

    from collections import Counter
    char_counts = Counter(all_chars)

    # Remove spaces and clean
    filtered_counts = {
        char: count
        for char, count in char_counts.items()
        if char.strip() != ""
    }

    # Top 15 characters (includes Marathi + numbers)
    top_chars = dict(
        sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    )

    # ---------------- AVERAGE ----------------
    avg_per_user = round(total / unique_users, 2) if unique_users > 0 else 0

    return render_template(
        "dashboard.html",
        total=total,
        unique_users=unique_users,
        avg_per_user=avg_per_user,
        top_users=top_users,
        daily_data=daily_data,
        top_chars=top_chars
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, date
import os
import re
import random
import time
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# pdf download
from flask import send_file, request
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_NAME = "database.db"


# profile upload data 
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---- Categories ----
INCOME_CATEGORIES = [
    "Salary", "Business", "Investments", "Rental Income",
    "Gifts", "Bonuses", "Refunds", "Other"
]


EXPENSE_CATEGORIES = [
    "Food & Dining", "Rent / Housing", "Transportation", "Health & Medical",
    "Entertainment", "Education", "Shopping", "Travel", "Utilities",
    "Insurance", "Investments", "Taxes", "Others"
]



# Quiz Question and Answer Option
# QUIZ_QUESTIONS = [

#     # 1️⃣ Japan City
#     {
#         "question": "Which is a major city in Japan?",
#         "options": [
#             "Tokyo",
#             "Yangon",
#             "Bangkok",
#             "Hanoi"
#         ],
#         "answer": "Tokyo"
#     },

#     # 2️⃣ Myanmar City
#     {
#         "question": "Which is a major city in Myanmar?",
#         "options": [
#             "Osaka",
#             "Yangon",
#             "Seoul",
#             "Beijing"
#         ],
#         "answer": "Yangon"
#     },

#     # 3️⃣ Japan Favourite Place
#     {
#         "question": "Which place is a famous tourist attraction in Japan?",
#         "options": [
#             "Mount Fuji",
#             "Bagan",
#             "Angkor Wat",
#             "Great Wall"
#         ],
#         "answer": "Mount Fuji"
#     },

#     # 4️⃣ Myanmar Favourite Place
#     {
#         "question": "Which place is a famous tourist attraction in Myanmar?",
#         "options": [
#             "Shwedagon Pagoda",
#             "Tokyo Tower",
#             "Inlay",
#             "Bagan"
#         ],
#         "answer": "Bagan"
#     },

#     # 5️⃣ Most Income Country in the World
#     {
#         "question": "Which country has the largest economy (highest income) in the world?",
#         "options": [
#             "United States",
#             "Japan",
#             "Germany",
#             "Myanmar"
#         ],
#         "answer": "United States"
#     },

#     # 6️⃣ Myanmar President
#     {
#         "question": "Who is the current President of Myanmar?",
#         "options": [
#             "Min Aung Hlaing",
#             "Win Myint",
#             "Joe Biden",
#             "U Thein Sein"
#         ],
#         "answer": "Min Aung Hlaing"
#     },

#     # 7️⃣ Japan President (Prime Minister)
#     {
#         "question": "Who is the Prime Minister of Japan?",
#         "options": [
#             "Fumio Kishida",
#             "Shinzo Abe",
#             "Joe Biden",
#             "Aung San Suu Kyi"
#         ],
#         "answer": "Fumio Kishida"
#     },

#     # 8️⃣ American President
#     {
#         "question": "Who is the President of the United States?",
#         "options": [
#             "Joe Biden",
#             "Donald Trump",
#             "Barack Obama",
#             "George Bush"
#         ],
#         "answer": "Joe Biden"
#     },

#     # 9️⃣ Myanmar Country Below Township (Example: Ward/Village Tract)
#     {
#         "question": "Which administrative level is below a township in Myanmar?",
#         "options": [
#             "Ward / Village Tract",
#             "Region",
#             "State",
#             "Country"
#         ],
#         "answer": "Ward / Village Tract"
#     },

#     # 🔟 Myanmar Country Above Township
#     {
#         "question": "Which administrative level is above a township in Myanmar?",
#         "options": [
#             "District",
#             "Ward",
#             "Village",
#             "Street"
#         ],
#         "answer": "District"
#     }

# ]

# timer for condition
QUIZ_TIME_LIMIT =60  # seconds
QUIZ_TOTAL_QUESTIONS = 10

# Quiz Question and Answer Option Updated
QUIZ_QUESTIONS = [

# ================= JAPAN =================
{
    "question": "Which is the capital city of Japan?",
    "options": ["Tokyo", "Osaka", "Kyoto", "Nagoya"],
    "answer": "Tokyo"
},
{
    "question": "Which city is famous for food in Japan?",
    "options": ["Osaka", "Sapporo", "Nara", "Hiroshima"],
    "answer": "Osaka"
},
{
    "question": "Which place is Japan famous for cherry blossoms?",
    "options": ["Kyoto", "Bagan", "Paris", "Yangon"],
    "answer": "Kyoto"
},
{
    "question": "What is the famous mountain in Japan?",
    "options": ["Mount Fuji", "Mount Everest", "Mount Popa", "Mount Kailash"],
    "answer": "Mount Fuji"
},
{
    "question": "Which city hosted the Tokyo Olympics?",
    "options": ["Tokyo", "Osaka", "Hiroshima", "Nagoya"],
    "answer": "Tokyo"
},
{
    "question": "Which sea surrounds Japan?",
    "options": ["Sea of Japan", "Red Sea", "Arabian Sea", "Black Sea"],
    "answer": "Sea of Japan"
},
{
    "question": "What is Japan's currency?",
    "options": ["Yen", "Won", "Dollar", "Euro"],
    "answer": "Yen"
},
{
    "question": "Who is the Prime Minister of Japan (recent)?",
    "options": ["Fumio Kishida", "Shinzo Abe", "Joe Biden", "Narendra Modi"],
    "answer": "Fumio Kishida"
},

# ================= MYANMAR =================
{
    "question": "What is the capital city of Myanmar?",
    "options": ["Naypyidaw", "Yangon", "Mandalay", "Bagan"],
    "answer": "Naypyidaw"
},
{
    "question": "Which city is the largest city in Myanmar?",
    "options": ["Yangon", "Mandalay", "Bago", "Taunggyi"],
    "answer": "Yangon"
},
{
    "question": "Which place is famous for ancient temples in Myanmar?",
    "options": ["Bagan", "Inlay", "Ngapali", "Hpa-An"],
    "answer": "Bagan"
},
{
    "question": "Which lake is a famous tourist place in Myanmar?",
    "options": ["Inlay Lake", "Victoria Lake", "Lake Biwa", "Tonle Sap"],
    "answer": "Inlay Lake"
},
{
    "question": "Which pagoda is famous in Yangon?",
    "options": ["Shwedagon Pagoda", "Ananda Pagoda", "Kyaiktiyo", "Sulamani"],
    "answer": "Shwedagon Pagoda"
},
{
    "question": "What is Myanmar's currency?",
    "options": ["Kyat", "Yen", "Baht", "Dollar"],
    "answer": "Kyat"
},
{
    "question": "Which sea is in Myanmar?",
    "options": ["Andaman Sea", "Red Sea", "Black Sea", "Mediterranean Sea"],
    "answer": "Andaman Sea"
},
# ================= WORLD =================
{
    "question": "Which country has the largest economy in the world?",
    "options": ["United States", "China", "Japan", "Germany"],
    "answer": "United States"
},
{
    "question": "Who is the President of the United States?",
    "options": ["Joe Biden", "Donald Trump", "Obama", "George Bush"],
    "answer": "Joe Biden"
},
{
    "question": "Which country uses the Dollar?",
    "options": ["United States", "Japan", "Myanmar", "Thailand"],
    "answer": "United States"
},
{
    "question": "Which country is famous for Eiffel Tower?",
    "options": ["France", "Italy", "Germany", "Spain"],
    "answer": "France"
},
{
    "question": "Which country has the largest population?",
    "options": ["China", "India", "USA", "Japan"],
    "answer": "China"
},
{
    "question": "Which ocean is the largest?",
    "options": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
    "answer": "Pacific Ocean"
},
{
    "question": "Which continent is Myanmar in?",
    "options": ["Asia", "Europe", "Africa", "Australia"],
    "answer": "Asia"
},

# ================= ADMINISTRATION (MYANMAR) =================
{
    "question": "Which administrative level is below a township in Myanmar?",
    "options": ["Ward / Village Tract", "District", "Region", "Country"],
    "answer": "Ward / Village Tract"
},
{
    "question": "Which administrative level is above a township in Myanmar?",
    "options": ["District", "Ward", "Village", "Street"],
    "answer": "District"
},
{
    "question": "Which is the highest administrative level in Myanmar?",
    "options": ["Country", "Township", "Village", "Ward"],
    "answer": "Country"
},

# ================= FUN & GENERAL =================
{
    "question": "Which app is used to manage income and expenses?",
    "options": ["Expense Tracker", "Facebook", "YouTube", "Game App"],
    "answer": "Expense Tracker"
},
{
    "question": "Which language is Flask written in?",
    "options": ["Python", "Java", "PHP", "C++"],
    "answer": "Python"
},
{
    "question": "Which database is commonly used with Flask?",
    "options": ["SQLite", "Excel", "Word", "PowerPoint"],
    "answer": "SQLite"
},
{
    "question": "What is HTML used for?",
    "options": ["Web pages", "Games only", "Databases", "Servers"],
    "answer": "Web pages"
},
{
    "question": "What does CSS control?",
    "options": ["Design & Style", "Logic", "Database", "Security"],
    "answer": "Design & Style"
},
{
    "question": "Which language is used with Flask templates?",
    "options": ["Jinja2", "React", "Angular", "Vue"],
    "answer": "Jinja2"
},
{
    "question": "Which feature helps users login securely?",
    "options": ["Session", "Print", "Alert", "Console"],
    "answer": "Session"
}

]



# ---- Initialize Database ----
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        avatar TEXT
        
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    conn.commit()
    conn.close()

init_db()

# ---- Home ----
@app.route("/")
def index():
    return redirect(url_for("login"))

#register
# EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"].strip()
#         email = request.form["email"].strip()
#         password = request.form["password"].strip()

#         # ---- Validation ----
#         if not username or not email or not password:
#             flash("All fields are required!", "danger")
#             return render_template("register.html")

#         if not EMAIL_REGEX.match(email):
#             flash("Invalid email format!", "danger")
#             return render_template("register.html")

#         if len(password) < 6:
#             flash("Password must be at least 6 characters long!", "danger")
#             return render_template("register.html")

#         # ---- Save to database ----
#         try:
#             conn = sqlite3.connect(DB_NAME)
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
#                 (username, email, password)
#             )
#             conn.commit()
#             conn.close()
#             flash("Registration successful! Please login.", "success")
#             return redirect(url_for("login"))
#         except sqlite3.IntegrityError:
#             flash("Username or email already exists!", "danger")
#             return render_template("register.html")

#     return render_template("register.html")

# test register
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # ---- Validation ----
        if not username or not email or not password:
            flash("All fields are required!", "danger")
            return render_template("register.html")

        if not EMAIL_REGEX.match(email):
            flash("Invalid email format!", "danger")
            return render_template("register.html")

        # if len(password) < 6:
        #     flash("Password must be at least 6 characters long!", "danger")
        #     return render_template("register.html")
        
        if not re.match(r"^(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{6,}$", password):
              flash("Password must be at least 6 characters long and include a number and a special character!",
                     "danger")
              return render_template("register.html")


        # ---- Save to database with password hash ----
        try:
            hashed_password = generate_password_hash(password)  # 🔑 hash password
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            
            conn.commit()
            conn.close()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "danger")
            return render_template("register.html")

    return render_template("register.html")


# login data 
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         avatar_file = request.files.get("avatar")

#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT id, username, avatar FROM users WHERE username=? AND password=?",
#             (username, password)
#         )
#         user = cursor.fetchone()

#         if user:
#             user_id = user[0]
#             filename = user[2]  # existing avatar filename

#             # Handle new avatar upload
#             if avatar_file and avatar_file.filename != "":
#                 from werkzeug.utils import secure_filename
#                 ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
#                 if "." in avatar_file.filename and avatar_file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS:
#                     filename = secure_filename(avatar_file.filename)
#                     avatar_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#                     avatar_file.save(avatar_path)

#                     # Update database with new avatar filename
#                     cursor.execute(
#                         "UPDATE users SET avatar=? WHERE id=?",
#                         (filename, user_id)
#                     )
#                     conn.commit()

#             conn.close()

#             # Store session info
#             session["user_id"] = user_id
#             session["username"] = user[1]
#             session["avatar"] = filename

#             flash(f"Welcome back, {user[1]}!", "success")
#             return redirect(url_for("dashboard"))

#         else:
#             conn.close()
#             flash("Invalid username or password!", "danger")

#     return render_template("login.html")

# test login 
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"].strip()
#         password = request.form["password"].strip()
       

#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT id, username, avatar FROM users WHERE username=? AND password=?",
#             (username, password)
#         )
#         user = cursor.fetchone()
#         conn.close()

#         if user and check_password_hash(user["password"], password):
#             session["user_id"] = user["id"]
#             session["username"] = user["username"]
#             flash("Login successful!", "success")
#             return redirect(url_for("dashboard"))
        
#         else:
#             flash("Username or password incorrect!", "danger")
#             return redirect(url_for("login"))

#     return render_template("login.html")

# test login update
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        avatar_file = request.files.get("avatar")  # optional avatar upload

        # --- Fetch user by username ---
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            flash("Invalid username or password!", "danger")
            return redirect(url_for("login"))

        # --- Verify password ---
        if not check_password_hash(user["password"], password):
            conn.close()
            flash("Invalid username or password!", "danger")
            return redirect(url_for("login"))

        user_id = user["id"]
        filename = user["avatar"]  # existing avatar in DB

        # --- Handle new avatar upload ---
        if avatar_file and avatar_file.filename != "":
            if allowed_file(avatar_file.filename):
                filename = secure_filename(avatar_file.filename)
                avatar_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                avatar_file.save(avatar_path)

                # Update avatar filename in DB
                cursor.execute("UPDATE users SET avatar=? WHERE id=?", (filename, user_id))
                conn.commit()
            else:
                flash("Invalid avatar file type!", "warning")

        conn.close()

        # --- Store session info ---
        session["user_id"] = user_id
        session["username"] = user["username"]
        session["avatar"] = filename

        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

# ---- Logout ----
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out!", "success")
    return redirect(url_for("login"))


# ---- Dashboard ----
# @app.route("/dashboard")
# def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    # Date filter
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Total income
    income_query = "SELECT SUM(amount) FROM income WHERE user_id=?"
    income_params = [user_id]
    if start_date and end_date:
        income_query += " AND date BETWEEN ? AND ?"
        income_params += [start_date, end_date]
    cursor.execute(income_query, income_params)
    total_income = cursor.fetchone()[0] or 0

    # Total expense
    expense_query = "SELECT SUM(amount) FROM expenses WHERE user_id=?"
    expense_params = [user_id]
    if start_date and end_date:
        expense_query += " AND date BETWEEN ? AND ?"
        expense_params += [start_date, end_date]
    cursor.execute(expense_query, expense_params)
    total_expense = cursor.fetchone()[0] or 0

    balance = total_income - total_expense

    # Income records
    income_select = "SELECT id, category, amount, date, description FROM income WHERE user_id=?"
    income_params = [user_id]
    if start_date and end_date:
        income_select += " AND date BETWEEN ? AND ?"
        income_params += [start_date, end_date]
    income_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
    income_params += [per_page, offset]
    cursor.execute(income_select, income_params)
    income_records = cursor.fetchall()

    # Income pagination
    count_income_query = "SELECT COUNT(*) FROM income WHERE user_id=?"
    count_income_params = [user_id]
    if start_date and end_date:
        count_income_query += " AND date BETWEEN ? AND ?"
        count_income_params += [start_date, end_date]
    cursor.execute(count_income_query, count_income_params)
    total_income_pages = (cursor.fetchone()[0] + per_page - 1) // per_page

    # Expense records
    expense_select = "SELECT id, category, amount, date, description FROM expenses WHERE user_id=?"
    expense_params = [user_id]
    if start_date and end_date:
        expense_select += " AND date BETWEEN ? AND ?"
        expense_params += [start_date, end_date]
    expense_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
    expense_params += [per_page, offset]
    cursor.execute(expense_select, expense_params)
    expense_records = cursor.fetchall()

    # Expense pagination
    count_expense_query = "SELECT COUNT(*) FROM expenses WHERE user_id=?"
    count_expense_params = [user_id]
    if start_date and end_date:
        count_expense_query += " AND date BETWEEN ? AND ?"
        count_expense_params += [start_date, end_date]
    cursor.execute(count_expense_query, count_expense_params)
    total_expense_pages = (cursor.fetchone()[0] + per_page - 1) // per_page

    conn.close()

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        income_records=income_records,
        expense_records=expense_records,
        page=page,
        total_income_pages=total_income_pages,
        total_expense_pages=total_expense_pages,
        start_date=start_date,
        end_date=end_date
    )


# test dashboard (currently use in)
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    # Filters
    filter_type = request.args.get("filter")  # weekly, monthly, yearly
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Handle filter type
    today = datetime.today()
    if filter_type == "weekly":
        start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif filter_type == "monthly":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif filter_type == "yearly":
        start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    # else keep start_date and end_date from query params if provided

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Total income
    income_query = "SELECT SUM(amount) FROM income WHERE user_id=?"
    income_params = [user_id]
    if start_date and end_date:
        income_query += " AND date BETWEEN ? AND ?"
        income_params += [start_date, end_date]
    cursor.execute(income_query, income_params)
    total_income = cursor.fetchone()[0] or 0

    # Total expense
    expense_query = "SELECT SUM(amount) FROM expenses WHERE user_id=?"
    expense_params = [user_id]
    if start_date and end_date:
        expense_query += " AND date BETWEEN ? AND ?"
        expense_params += [start_date, end_date]
    cursor.execute(expense_query, expense_params)
    total_expense = cursor.fetchone()[0] or 0

    balance = total_income - total_expense

    # Income records with pagination
    income_select = "SELECT id, category, amount, date, description FROM income WHERE user_id=?"
    income_params = [user_id]
    if start_date and end_date:
        income_select += " AND date BETWEEN ? AND ?"
        income_params += [start_date, end_date]
    income_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
    income_params += [per_page, offset]
    cursor.execute(income_select, income_params)
    income_records = cursor.fetchall()

    # Income pagination
    count_income_query = "SELECT COUNT(*) FROM income WHERE user_id=?"
    count_income_params = [user_id]
    if start_date and end_date:
        count_income_query += " AND date BETWEEN ? AND ?"
        count_income_params += [start_date, end_date]
    cursor.execute(count_income_query, count_income_params)
    total_income_pages = (cursor.fetchone()[0] + per_page - 1) // per_page

    # Expense records with pagination
    expense_select = "SELECT id, category, amount, date, description FROM expenses WHERE user_id=?"
    expense_params = [user_id]
    if start_date and end_date:
        expense_select += " AND date BETWEEN ? AND ?"
        expense_params += [start_date, end_date]
    expense_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
    expense_params += [per_page, offset]
    cursor.execute(expense_select, expense_params)
    expense_records = cursor.fetchall()

    # Expense pagination
    count_expense_query = "SELECT COUNT(*) FROM expenses WHERE user_id=?"
    count_expense_params = [user_id]
    if start_date and end_date:
        count_expense_query += " AND date BETWEEN ? AND ?"
        count_expense_params += [start_date, end_date]
    cursor.execute(count_expense_query, count_expense_params)
    total_expense_pages = (cursor.fetchone()[0] + per_page - 1) // per_page

    conn.close()

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        income_records=income_records,
        expense_records=expense_records,
        page=page,
        total_income_pages=total_income_pages,
        total_expense_pages=total_expense_pages,
        start_date=start_date,
        end_date=end_date,
        filter_type=filter_type
    )


# test dashboard updated
# @app.route("/dashboard")
# def dashboard():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     user_id = session["user_id"]

#     # ----------------- Filters -----------------
#     filter_type = request.args.get("filter")  # weekly, monthly, yearly
#     start_date = request.args.get("start_date")
#     end_date = request.args.get("end_date")

#     # Handle quick filter
#     today = datetime.today()
#     if filter_type == "weekly":
#         start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
#         end_date = today.strftime("%Y-%m-%d")
#     elif filter_type == "monthly":
#         start_date = today.replace(day=1).strftime("%Y-%m-%d")
#         end_date = today.strftime("%Y-%m-%d")
#     elif filter_type == "yearly":
#         start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
#         end_date = today.strftime("%Y-%m-%d")

#     # ----------------- Pagination -----------------
#     page = request.args.get("page", 1, type=int)
#     per_page = 5
#     offset = (page - 1) * per_page

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     # ----------------- Total Income -----------------
#     income_query = "SELECT SUM(amount) FROM income WHERE user_id=?"
#     income_params = [user_id]
#     if start_date and end_date:
#         income_query += " AND date BETWEEN ? AND ?"
#         income_params += [start_date, end_date]
#     cursor.execute(income_query, income_params)
#     total_income = cursor.fetchone()[0] or 0

#     # ----------------- Total Expense -----------------
#     expense_query = "SELECT SUM(amount) FROM expenses WHERE user_id=?"
#     expense_params = [user_id]
#     if start_date and end_date:
#         expense_query += " AND date BETWEEN ? AND ?"
#         expense_params += [start_date, end_date]
#     cursor.execute(expense_query, expense_params)
#     total_expense = cursor.fetchone()[0] or 0

#     balance = total_income - total_expense

#     # ----------------- Income Records -----------------
#     income_select = "SELECT id, category, amount, date, description FROM income WHERE user_id=?"
#     income_params = [user_id]
#     if start_date and end_date:
#         income_select += " AND date BETWEEN ? AND ?"
#         income_params += [start_date, end_date]
#     income_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
#     income_params += [per_page, offset]
#     cursor.execute(income_select, income_params)
#     income_records = cursor.fetchall()

#     # ----------------- Income Pagination -----------------
#     count_income_query = "SELECT COUNT(*) FROM income WHERE user_id=?"
#     count_income_params = [user_id]
#     if start_date and end_date:
#         count_income_query += " AND date BETWEEN ? AND ?"
#         count_income_params += [start_date, end_date]
#     cursor.execute(count_income_query, count_income_params)
#     total_income_pages = (cursor.fetchone()[0] + per_page - 1) // per_page

#     # ----------------- Expense Records -----------------
#     expense_select = "SELECT id, category, amount, date, description FROM expenses WHERE user_id=?"
#     expense_params = [user_id]
#     if start_date and end_date:
#         expense_select += " AND date BETWEEN ? AND ?"
#         expense_params += [start_date, end_date]
#     expense_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
#     expense_params += [per_page, offset]
#     cursor.execute(expense_select, expense_params)
#     expense_records = cursor.fetchall()

#     # ----------------- Expense Pagination -----------------
#     count_expense_query = "SELECT COUNT(*) FROM expenses WHERE user_id=?"
#     count_expense_params = [user_id]
#     if start_date and end_date:
#         count_expense_query += " AND date BETWEEN ? AND ?"
#         count_expense_params += [start_date, end_date]
#     cursor.execute(count_expense_query, count_expense_params)
#     total_expense_pages = (cursor.fetchone()[0] + per_page - 1) // per_page

#     conn.close()

#     return render_template(
#         "dashboard.html",
#         total_income=total_income,
#         total_expense=total_expense,
#         balance=balance,
#         income_records=income_records,
#         expense_records=expense_records,
#         page=page,
#         total_income_pages=total_income_pages,
#         total_expense_pages=total_expense_pages,
#         start_date=start_date,
#         end_date=end_date,
#         filter_type=filter_type
#     )


# test dashboard updated 1()
# @app.route("/dashboard")
# def dashboard():
#     user_id = session.get("user_id")
#     start_date = request.args.get("start_date")
#     end_date = request.args.get("end_date")
#     filter_type = request.args.get("filter")

#     # Pagination parameters
#     income_page = int(request.args.get("income_page", 1))
#     expense_page = int(request.args.get("expense_page", 1))
#     per_page = 5  # records per page

#     # Fetch Income records
#     income_query = "SELECT * FROM income WHERE user_id=?"
#     params = [user_id]
#     if start_date:
#         income_query += " AND date >= ?"
#         params.append(start_date)
#     if end_date:
#         income_query += " AND date <= ?"
#         params.append(end_date)
#     # execute query and get all income records
#     income_records_all = cursor.execute(income_query, params).fetchall()
    
#     total_income = sum(rec[2] for rec in income_records_all)  # assuming amount at index 2

#     # Pagination for Income
#     income_total_pages = (len(income_records_all) + per_page - 1) // per_page
#     income_records = income_records_all[(income_page-1)*per_page : income_page*per_page]

#     # Fetch Expense records
#     expense_query = "SELECT * FROM expense WHERE user_id=?"
#     params = [user_id]
#     if start_date:
#         expense_query += " AND date >= ?"
#         params.append(start_date)
#     if end_date:
#         expense_query += " AND date <= ?"
#         params.append(end_date)
#     expense_records_all = cursor.execute(expense_query, params).fetchall()
    
#     total_expense = sum(rec[2] for rec in expense_records_all)

#     # Pagination for Expense
#     expense_total_pages = (len(expense_records_all) + per_page - 1) // per_page
#     expense_records = expense_records_all[(expense_page-1)*per_page : expense_page*per_page]

#     # Balance
#     balance = total_income - total_expense

#     return render_template("dashboard.html",
#                            total_income=total_income,
#                            total_expense=total_expense,
#                            balance=balance,
#                            income_records=income_records,
#                            expense_records=expense_records,
#                            income_page=income_page,
#                            expense_page=expense_page,
#                            income_total_pages=income_total_pages,
#                            expense_total_pages=expense_total_pages,
#                            start_date=start_date,
#                            end_date=end_date,
#                            filter_type=filter_type)


# add-income
@app.route("/add_income", methods=["GET","POST"])
def add_income():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]
        date_input = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO income(user_id,date,category,amount,description) VALUES(?,?,?,?,?)",
            (session["user_id"], date_input, category, amount, description)
        )
        conn.commit()
        conn.close()

        flash("Income added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "income_form.html",
        mode="add",
        categories=INCOME_CATEGORIES,
        current_date=date.today().strftime("%Y-%m-%d")
    )


# add expense 
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]
        date_input = request.form.get("date")
        confirm = request.form.get("confirm")  # <-- confirm flag

        # Calculate balance
        cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
        total_income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (session["user_id"],))
        total_expense = cursor.fetchone()[0] or 0

        available_balance = total_income - total_expense

        # ❌ BLOCK
        if amount > available_balance:
            flash(f"Expense exceeds available balance ({available_balance})!", "danger")
            conn.close()
            return redirect(url_for("add_expense"))

        # ⚠ CONFIRM REQUIRED
        if amount == available_balance and confirm != "yes":
            flash(
                "This expense will use ALL your remaining balance. Please confirm.",
                "warning"
            )
            conn.close()
            return render_template(
                "expense_form.html",
                categories=EXPENSE_CATEGORIES,
                current_date=date_input,
                mode="add",
                show_confirm=True,
                form_data=request.form
            )

        # ✅ INSERT
        cursor.execute(
            "INSERT INTO expenses(user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], date_input, category, amount, description)
        )
        conn.commit()
        conn.close()

        flash("Expense added successfully!", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template(
        "expense_form.html",
        categories=EXPENSE_CATEGORIES,
        current_date=date.today().strftime("%Y-%m-%d"),
        mode="add",
        show_confirm=False
    )


# add expense test // test expense not working
# @app.route("/add_expense", methods=["GET", "POST"])
# def add_expense():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     if request.method == "POST":
#         category = request.form.get("category", "").strip()
#         amount_str = request.form.get("amount", "0").strip()
#         description = request.form.get("description", "").strip()
#         date_input = request.form.get("date", date.today().strftime("%Y-%m-%d"))
#         confirm = request.form.get("confirm")  # Checkbox confirm

#         # Validate amount
#         try:
#             amount = float(amount_str)
#             if amount <= 0:
#                 raise ValueError
#         except ValueError:
#             flash("Please enter a valid positive amount!", "danger")
#             conn.close()
#             return render_template(
#                 "expense_form.html",
#                 categories=EXPENSE_CATEGORIES,
#                 current_date=date_input,
#                 mode="add",
#                 show_confirm=False,
#                 form_data=request.form
#             )

#         # Calculate available balance
#         cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
#         total_income = cursor.fetchone()[0] or 0

#         cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (session["user_id"],))
#         total_expense = cursor.fetchone()[0] or 0

#         available_balance = total_income - total_expense

#         # BLOCK if expense exceeds balance
#         if amount > available_balance:
#             flash(f"Expense exceeds available balance ({available_balance})!", "danger")
#             conn.close()
#             return redirect(url_for("add_expense"))

#         # CONFIRM if using all balance
#         if amount == available_balance and confirm != "yes":
#             flash("This expense will use ALL your remaining balance. Please confirm.", "warning")
#             conn.close()
#             return render_template(
#                 "expense_form.html",
#                 categories=EXPENSE_CATEGORIES,
#                 current_date=date_input,
#                 mode="add",
#                 show_confirm=True,
#                 form_data=request.form
#             )

#         # INSERT expense
#         cursor.execute(
#             "INSERT INTO expenses(user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
#             (session["user_id"], date_input, category, amount, description)
#         )
#         conn.commit()
#         conn.close()

#         flash("Expense added successfully!", "success")
#         return redirect(url_for("dashboard"))

#     # GET request
#     conn.close()
#     return render_template(
#         "expense_form.html",
#         categories=EXPENSE_CATEGORIES,
#         current_date=date.today().strftime("%Y-%m-%d"),
#         mode="add",
#         show_confirm=False,
#         form_data=None
#     )

# edit-income
@app.route("/edit_income/<int:income_id>", methods=["GET","POST"])
def edit_income(income_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]
        date_input = request.form.get("date")

        cursor.execute("""
            UPDATE income
            SET date=?, category=?, amount=?, description=?
            WHERE id=? AND user_id=?
        """, (date_input, category, amount, description, income_id, session["user_id"]))

        conn.commit()
        conn.close()

        flash("Income updated successfully!", "success")
        return redirect(url_for("dashboard"))

    cursor.execute("""
        SELECT date, category, amount, description
        FROM income
        WHERE id=? AND user_id=?
    """, (income_id, session["user_id"]))

    record = cursor.fetchone()
    conn.close()

    if not record:
        flash("Record not found!", "danger")
        return redirect(url_for("dashboard"))

    return render_template(
        "income_form.html",
        mode="edit",
        categories=INCOME_CATEGORIES,
        record=record
    )

# ---- Delete Income ----
@app.route("/delete_income/<int:income_id>")
def delete_income(income_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id=? AND user_id=?", (income_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Income deleted!", "success")
    return redirect(url_for("dashboard"))

# ---- Edit Expense ----
@app.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        date_input = request.form.get("date")
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()
       

        # ✅ VALIDATION
        if not amount_str:
            flash("Amount is required!", "danger")
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        try:
            amount = float(amount_str)
        except ValueError:
            flash("Invalid amount value!", "danger")
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        if amount <= 0:
            flash("Amount must be greater than zero!", "danger")
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        # ---- BALANCE CHECK (exclude current expense) ----
        cursor.execute(
            "SELECT SUM(amount) FROM income WHERE user_id=?",
            (session["user_id"],)
        )
        total_income = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id=? AND id<>?",
            (session["user_id"], expense_id)
        )
        total_expense_except_current = cursor.fetchone()[0] or 0

        available_balance = total_income - total_expense_except_current

        if amount > available_balance:
            flash(
                f"Expense exceeds available balance ({available_balance})!",
                "danger"
            )
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        # ---- UPDATE EXPENSE ----
        cursor.execute(
            """
            UPDATE expenses
            SET date=?, category=?, amount=?, description=?
            WHERE id=? AND user_id=?
            """,
            (date_input,category, amount, description, expense_id, session["user_id"])
        )

        conn.commit()
        conn.close()

        flash("Expense updated successfully!", "success")
        return redirect(url_for("dashboard"))

    # ---- GET REQUEST (LOAD RECORD) ----
    cursor.execute(
        """
        SELECT date,category, amount, description
        FROM expenses
        WHERE id=? AND user_id=?
        """,
        (expense_id, session["user_id"])
    )
    record = cursor.fetchone()
    conn.close()

    if not record:
        flash("Record not found!", "danger")
        return redirect(url_for("dashboard"))

    return render_template(
        "expense_form.html",
        categories=EXPENSE_CATEGORIES,
        record=record,
        mode="edit"
    )

# ---- Delete Expense ----
@app.route("/delete_expense/<int:expense_id>")
def delete_expense(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Expense deleted!", "success")
    return redirect(url_for("dashboard"))



# view by chart
@app.route("/charts", methods=["GET", "POST"])
def charts():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ---------- INCOME ----------
    if start_date and end_date:
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM income
            WHERE user_id=? AND date BETWEEN ? AND ?
            GROUP BY category
        """, (session["user_id"], start_date, end_date))
    else:
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM income
            WHERE user_id=?
            GROUP BY category
        """, (session["user_id"],))

    income_data = cursor.fetchall()

    # ---------- EXPENSE ----------
    if start_date and end_date:
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE user_id=? AND date BETWEEN ? AND ?
            GROUP BY category
        """, (session["user_id"], start_date, end_date))
    else:
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE user_id=?
            GROUP BY category
        """, (session["user_id"],))

    expense_data = cursor.fetchall()
    
    
    # total income,expense,balance
     # Total income
    income_query = "SELECT SUM(amount) FROM income WHERE user_id=?"
    income_params = [user_id]
    if start_date and end_date:
        income_query += " AND date BETWEEN ? AND ?"
        income_params += [start_date, end_date]
    cursor.execute(income_query, income_params)
    total_income = cursor.fetchone()[0] or 0

    # Total expense
    expense_query = "SELECT SUM(amount) FROM expenses WHERE user_id=?"
    expense_params = [user_id]
    if start_date and end_date:
        expense_query += " AND date BETWEEN ? AND ?"
        expense_params += [start_date, end_date]
    cursor.execute(expense_query, expense_params)
    total_expense = cursor.fetchone()[0] or 0
    
    balance = total_income - total_expense

    conn.close()

    income_labels = [row[0] for row in income_data]
    income_values = [row[1] for row in income_data]

    expense_labels = [row[0] for row in expense_data]
    expense_values = [row[1] for row in expense_data]

    return render_template(
        "charts.html",
        income_labels=income_labels,
        income_values=income_values,
        expense_labels=expense_labels,
        expense_values=expense_values,
        start_date=start_date,
        end_date=end_date,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
        
    )



# download report pdf file 
@app.route("/download/report/pdf")
def download_report_pdf():
    if "user_id" not in session:
        return redirect(url_for("login"))

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    condition = ""
    params = [session["user_id"]]

    if start_date and end_date:
        condition = "AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    # ---------- Income ----------
    cursor.execute(f"""
        SELECT date, category, amount, description
        FROM income
        WHERE user_id=? {condition}
        ORDER BY date
    """, params)
    income_records = cursor.fetchall()

    # ---------- Expense ----------
    cursor.execute(f"""
        SELECT date, category, amount, description
        FROM expenses
        WHERE user_id=? {condition}
        ORDER BY date
    """, params)
    expense_records = cursor.fetchall()

    conn.close()

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # ---------- Title ----------
    elements.append(Paragraph(
        f"<b>Income & Expense Report</b><br/>Generated: {date.today()}",
        styles["Title"]
    ))

    if start_date and end_date:
        elements.append(Paragraph(
            f"Period: {start_date} to {end_date}",
            styles["Normal"]
        ))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---------- Income Table ----------
    elements.append(Paragraph("<b>Income Records</b>", styles["Heading2"]))

    income_table = [["Date", "Category", "Amount", "Description"]]
    for r in income_records:
        income_table.append(list(r))

    if len(income_table) == 1:
        income_table.append(["-", "-", "-", "No records"])

    elements.append(Table(income_table, colWidths=[70, 90, 70, 180],
        style=[
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgreen),
            ("ALIGN", (2,1), (2,-1), "RIGHT")
        ]
    ))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---------- Expense Table ----------
    elements.append(Paragraph("<b>Expense Records</b>", styles["Heading2"]))

    expense_table = [["Date", "Category", "Amount", "Description"]]
    for r in expense_records:
        expense_table.append(list(r))

    if len(expense_table) == 1:
        expense_table.append(["-", "-", "-", "No records"])

    elements.append(Table(expense_table, colWidths=[70, 90, 70, 180],
        style=[
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.salmon),
            ("ALIGN", (2,1), (2,-1), "RIGHT")
        ]
    ))

    pdf.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="income_expense_history_report.pdf",
        mimetype="application/pdf"
    )
    
    
    
#profile page
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Connect to DB
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch user info
    cursor.execute("SELECT username, email, avatar FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        flash("User not found!", "danger")
        return redirect(url_for("dashboard"))

    # Fetch total income
    cursor.execute("SELECT SUM(amount) as total_income FROM income WHERE user_id=?", (user_id,))
    total_income_row = cursor.fetchone()
    total_income = total_income_row["total_income"] if total_income_row["total_income"] else 0

    # Fetch total expense
    cursor.execute("SELECT SUM(amount) as total_expense FROM expenses WHERE user_id=?", (user_id,))
    total_expense_row = cursor.fetchone()
    total_expense = total_expense_row["total_expense"] if total_expense_row["total_expense"] else 0
    balance = total_income - total_expense
    conn.close()

    return render_template(
        "profile.html",
        user=user,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )
    
    
#edit profile
@app.route("/profile/edit")
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, email FROM users WHERE id=?",
        (session["user_id"],)
    )
    user = cursor.fetchone()
    conn.close()

    return render_template("edit_profile.html", user=user)

# update profile
# @app.route("/profile/update", methods=["POST"])
# def update_profile():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     user_id = session["user_id"]

#     username = request.form["username"]
#     old_password = request.form["old_password"]
#     new_password = request.form["new_password"]

#     conn = sqlite3.connect(DB_NAME)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()

#     cursor.execute(
#         "SELECT password FROM users WHERE id=?",
#         (user_id,)
#     )
#     user = cursor.fetchone()

#     if not user or not check_password_hash(user["password"], old_password):
#         conn.close()
#         flash("Old password is incorrect!", "danger")
#         return redirect(url_for("edit_profile"))

#     # Update username
#     cursor.execute(
#         "UPDATE users SET username=? WHERE id=?",
#         (username, user_id)
#     )

#     # Update password only if new password entered
#     if new_password.strip():
#         hashed_password = generate_password_hash(new_password)
#         cursor.execute(
#             "UPDATE users SET password=? WHERE id=?",
#             (hashed_password, user_id)
#         )

#     conn.commit()
#     conn.close()

#     flash("Profile updated successfully!", "success")
#     return redirect(url_for("profile"))

# update profile test this is real world test but this in error working currently use in (no)
# @app.route("/profile/update", methods=["POST"])
# def update_profile():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     user_id = session["user_id"]
#     username = request.form["username"].strip()
#     old_password = request.form["old_password"].strip()
#     new_password = request.form["new_password"].strip()

#     conn = sqlite3.connect(DB_NAME)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
#     user = cursor.fetchone()

#     if not user or not check_password_hash(user["password"], old_password):
#         conn.close()
#         flash("Old password is incorrect!", "danger")
#         return redirect(url_for("edit_profile"))

#     # Update username
#     cursor.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))

#     # Update password if new one entered
#     if new_password:
#         hashed_password = generate_password_hash(new_password)
#         cursor.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))

#     conn.commit()
#     conn.close()

#     flash("Profile updated successfully!", "success")
#     return redirect(url_for("profile"))


# updated profile test rehersal (currently use in(yes) working )
@app.route("/profile/update", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    username = request.form["username"].strip()
    old_password = request.form["old_password"].strip()
    new_password = request.form["new_password"].strip()

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1️⃣ Get current user
    cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user or not check_password_hash(user["password"], old_password):
        conn.close()
        flash("Old password is incorrect!", "danger")
        return redirect(url_for("edit_profile"))

    # 2️⃣ Check if new username already exists for another user
    cursor.execute("SELECT id FROM users WHERE username=? AND id!=?", (username, user_id))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        flash("Username already taken! Please choose another.", "danger")
        return redirect(url_for("edit_profile"))

    # 3️⃣ Update username
    cursor.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))

    # 4️⃣ Update password if new one entered
    if new_password:
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))

    conn.commit()
    conn.close()

    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile"))


# Quiz Option Adding Route
# @app.route("/quiz", methods=["GET", "POST"])
# def quiz():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     if "quiz_index" not in session:
#         session["quiz_index"] = 0
#         session["quiz_score"] = 0

#     index = session["quiz_index"]

#     if request.method == "POST":
#         selected = request.form.get("option")
#         correct = QUIZ_QUESTIONS[index]["answer"]

#         if selected == correct:
#             session["quiz_score"] += 1

#         session["quiz_index"] += 1
#         return redirect(url_for("quiz"))

#     if index >= len(QUIZ_QUESTIONS):
#         return redirect(url_for("quiz_result"))

#     return render_template(
#         "quiz.html",
#         question=QUIZ_QUESTIONS[index],
#         current=index + 1,
#         total=len(QUIZ_QUESTIONS)
#     )


# quiz updated (currently use in yes)
# @app.route("/quiz", methods=["GET", "POST"])
# def quiz():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     # Initialize quiz session
#     if "quiz_index" not in session or "quiz_questions" not in session:
#         # Pick 10 random questions from the pool
#         session["quiz_questions"] = random.sample(QUIZ_QUESTIONS, 10)
#         session["quiz_index"] = 0
#         session["quiz_score"] = 0

#     index = session["quiz_index"]
#     quiz_questions = session["quiz_questions"]

#     # If POST, check answer
#     if request.method == "POST":
#         selected = request.form.get("option")
#         correct = quiz_questions[index]["answer"]

#         if selected == correct:
#             session["quiz_score"] += 1

#         session["quiz_index"] += 1
#         index = session["quiz_index"]

#         if index >= len(quiz_questions):
#             return redirect(url_for("quiz_result"))

#         return redirect(url_for("quiz"))

#     # Show current question
#     if index < len(quiz_questions):
#         question = quiz_questions[index]
#         return render_template(
#             "quiz.html",
#             question=question,
#             current=index + 1,
#             total=len(quiz_questions)
#         )

#     return redirect(url_for("quiz_result"))


# quiz updated 1(currently use in no)
# @app.route("/quiz", methods=["GET", "POST"])
# def quiz():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     # Initialize quiz session
#     if "quiz_index" not in session or "quiz_questions" not in session:
#         session["quiz_questions"] = random.sample(QUIZ_QUESTIONS, 10)
#         session["quiz_index"] = 0
#         session["quiz_score"] = 0

#     index = session["quiz_index"]
#     quiz_questions = session["quiz_questions"]

#     # If user tries to go back manually
#     if index >= len(quiz_questions):
#         return redirect(url_for("quiz_result"))

#     # Handle POST answer
#     if request.method == "POST":
#         selected = request.form.get("option")
#         correct = quiz_questions[index]["answer"]

#         if selected == correct:
#             session["quiz_score"] += 1

#         session["quiz_index"] += 1
#         index = session["quiz_index"]

#         if index >= len(quiz_questions):
#             return redirect(url_for("quiz_result"))

#         return redirect(url_for("quiz"))

#     # Show current question
#     question = quiz_questions[index]
#     return render_template(
#         "quiz.html",
#         question=question,
#         current=index + 1,
#         total=len(quiz_questions),
#         timestamp=datetime.now().timestamp() ) # For cache-busting


# quiz updated 2
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # 🔐 Initialize quiz safely
    if (
        "quiz_questions" not in session
        or "quiz_start_time" not in session
        or "quiz_index" not in session
    ):
        # session.clear()  # optional but safe
        session["quiz_questions"] = random.sample(QUIZ_QUESTIONS, QUIZ_TOTAL_QUESTIONS)
        session["quiz_index"] = 0
        session["quiz_score"] = 0
        session["quiz_start_time"] = time.time()

    # ⏱ Safe timer check
    start_time = session.get("quiz_start_time")

    if not start_time:
        return redirect(url_for("quiz_reset"))

    elapsed_time = int(time.time() - start_time)
    remaining_time = QUIZ_TIME_LIMIT - elapsed_time

    if remaining_time <= 0:
        return redirect(url_for("quiz_result"))

    index = session["quiz_index"]
    quiz_questions = session["quiz_questions"]

    # POST → Answer submitted
    if request.method == "POST":
        selected = request.form.get("option")

        if index < len(quiz_questions):
            correct = quiz_questions[index]["answer"]
            if selected == correct:
                session["quiz_score"] += 1

            session["quiz_index"] += 1

        if session["quiz_index"] >= len(quiz_questions):
            return redirect(url_for("quiz_result"))

        return redirect(url_for("quiz"))

    # GET → Show question
    question = quiz_questions[index]

    return render_template(
        "quiz.html",
        question=question,
        current=index + 1,
        total=len(quiz_questions),
        remaining_time=remaining_time
    )
# @app.route("/quiz/result")
# def quiz_result():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     score = session.get("quiz_score", 0)
#     total = len(QUIZ_QUESTIONS)

#     return render_template(
#         "quiz_result.html",
#         score=score,
#         total=total
#     )

# quiz result updated (currently use in yes)
# @app.route("/quiz/result")
# def quiz_result():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     score = session.get("quiz_score", 0)
#     total = len(session.get("quiz_questions", []))

#     # Clear quiz session after showing result
#     session.pop("quiz_index", None)
#     session.pop("quiz_score", None)
#     session.pop("quiz_questions", None)

#     return render_template(
#         "quiz_result.html",
#         score=score,
#         total=total
#     )



# # @app.route("/quiz/reset")
# # def quiz_reset():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     session.pop("quiz_index", None)
#     session.pop("quiz_score", None)
#     return redirect(url_for("quiz"))


# quiz updated 2
@app.route("/quiz/result")
def quiz_result():
    if "user_id" not in session:
        return redirect(url_for("login"))

    score = session.get("quiz_score", 0)
    total = len(session.get("quiz_questions", []))

    return render_template("quiz_result.html", score=score, total=total)


# quiz reset updated (currently use in yes )
# @app.route("/quiz/reset")
# def quiz_reset():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     # Reset quiz session
#     session.pop("quiz_index", None)
#     session.pop("quiz_score", None)
#     session.pop("quiz_questions", None)

#     return redirect(url_for("quiz"))

# quiz updated 2
@app.route("/quiz/reset")
def quiz_reset():
    session.pop("quiz_questions", None)
    session.pop("quiz_index", None)
    session.pop("quiz_score", None)
    session.pop("quiz_start_time", None)
    return redirect(url_for("quiz"))



@app.route("/quiz/quit")
def quiz_quit():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Clear quiz session data
    session.pop("quiz_questions", None)
    session.pop("quiz_index", None)
    session.pop("quiz_score", None)
    session.pop("quiz_start_time", None)

    return redirect(url_for("dashboard"))

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True)
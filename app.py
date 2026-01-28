from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, date
import os
import re
from werkzeug.utils import secure_filename

# pdf download
from flask import send_file, request
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import sqlite3
from datetime import date

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

# ---- Register ----
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         try:
#             conn = sqlite3.connect(DB_NAME)
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO users(username,password) VALUES(?,?)", (username,password))
#             conn.commit()
#             conn.close()
#             flash("Registration successful! Please login.", "success")
#             return redirect(url_for("login"))
#         except sqlite3.IntegrityError:
#             flash("Username already exists!", "danger")
#     return render_template("register.html")


# new register 
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         email = request.form["email"]
#         password = request.form["password"]
#         # avatar_file = request.files.get("avatar")

#         # # Handle avatar upload
#         # if avatar_file and allowed_file(avatar_file.filename):
#         #     filename = secure_filename(avatar_file.filename)
#         #     avatar_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#         #     avatar_file.save(avatar_path)
#         # else:
#         #     filename = None  # optional if no image uploaded

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

#     return render_template("register.html")

# new register 1
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

        if len(password) < 6:
            flash("Password must be at least 6 characters long!", "danger")
            return render_template("register.html")

        # Optional: handle avatar upload
        # avatar_file = request.files.get("avatar")
        # if avatar_file and allowed_file(avatar_file.filename):
        #     filename = secure_filename(avatar_file.filename)
        #     avatar_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # else:
        #     filename = None

        # ---- Save to database ----
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "danger")
            return render_template("register.html")

    return render_template("register.html")

# ---- Login ----
# @app.route("/login", methods=["GET","POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
#         user = cursor.fetchone()
#         conn.close()
        
        
#         if user:
#             session["user_id"] = user[0]
#             session["username"] = user[1]
#             return redirect(url_for("dashboard"))
        
        
#         else:
#             flash("Invalid credentials!", "danger")
#     return render_template("login.html")



# new login data 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        avatar_file = request.files.get("avatar")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, avatar FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            filename = user[2]  # existing avatar filename

            # Handle new avatar upload
            if avatar_file and avatar_file.filename != "":
                from werkzeug.utils import secure_filename
                ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
                if "." in avatar_file.filename and avatar_file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS:
                    filename = secure_filename(avatar_file.filename)
                    avatar_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    avatar_file.save(avatar_path)

                    # Update database with new avatar filename
                    cursor.execute(
                        "UPDATE users SET avatar=? WHERE id=?",
                        (filename, user_id)
                    )
                    conn.commit()

            conn.close()

            # Store session info
            session["user_id"] = user_id
            session["username"] = user[1]
            session["avatar"] = filename

            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for("dashboard"))

        else:
            conn.close()
            flash("Invalid username or password!", "danger")

    return render_template("login.html")

# ---- Logout ----
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out!", "info")
    return redirect(url_for("login"))

# ---- Dashboard ----
@app.route("/dashboard")
def dashboard():
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

# ---- Add Income ----
# @app.route("/add_income", methods=["GET","POST"])
# def add_income():
#     if "user_id" not in session:
#         return redirect(url_for("login"))
#     if request.method == "POST":
#         category = request.form["category"]
#         amount = float(request.form["amount"])
#         description = request.form["description"]
#         date_input = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")
#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO income(user_id,date,category,amount,description) VALUES(?,?,?,?,?)",
#             (session["user_id"], date_input, category, amount, description)
#         )
#         conn.commit()
#         conn.close()
#         flash("Income added successfully!", "success")
#         return redirect(url_for("dashboard"))
#     return render_template("add_income.html", categories=INCOME_CATEGORIES, current_date=date.today().strftime("%Y-%m-%d"))
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

# ---- Add Expense ----
# @app.route("/add_expense", methods=["GET","POST"])
# def add_expense():
#     if "user_id" not in session:
#         return redirect(url_for("login"))
#     if request.method == "POST":
#         category = request.form["category"]
#         amount = float(request.form["amount"])
#         description = request.form["description"]
#         date_input = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")

#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()

#         # Balance check
#         cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
#         total_income = cursor.fetchone()[0] or 0
#         cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (session["user_id"],))
#         total_expense = cursor.fetchone()[0] or 0
#         available_balance = total_income - total_expense

#         if total_income == 0:
#             flash("Add income first!", "danger")
#             conn.close()
#             return redirect(url_for("add_expense"))
#         if amount > available_balance:
#             flash(f"Expense exceeds available balance ({available_balance})!", "danger")
#             conn.close()
#             return redirect(url_for("add_expense"))

#         cursor.execute(
#             "INSERT INTO expenses(user_id,date,category,amount,description) VALUES(?,?,?,?,?)",
#             (session["user_id"], date_input, category, amount, description)
#         )
#         conn.commit()
#         conn.close()
#         flash("Expense added successfully!", "success")
#         return redirect(url_for("dashboard"))
#     return render_template("add_expense.html", categories=EXPENSE_CATEGORIES, current_date=date.today().strftime("%Y-%m-%d"))
# @app.route("/add_expense", methods=["GET", "POST"])
# def add_expense():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     if request.method == "POST":
#         category = request.form["category"]
#         amount = float(request.form["amount"])
#         description = request.form["description"]
#         date_input = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")

#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()

#         # ---- BALANCE CHECK ----
#         cursor.execute(
#             "SELECT SUM(amount) FROM income WHERE user_id=?",
#             (session["user_id"],)
#         )
#         total_income = cursor.fetchone()[0] or 0

#         cursor.execute(
#             "SELECT SUM(amount) FROM expenses WHERE user_id=?",
#             (session["user_id"],)
#         )
#         total_expense = cursor.fetchone()[0] or 0

#         available_balance = total_income - total_expense

#         if total_income == 0:
#             flash("Add income first!", "danger")
#             conn.close()
#             return redirect(url_for("add_expense"))
        
#         # if amount == available_balance:
#         #     flash(f"Are you sure want to use for my income only for this reason!","warning")
#         #     conn.close()
            

#         if amount > available_balance:
#             flash(
#                 f"Expense exceeds available balance ({available_balance})!",
#                 "danger"
#             )
#             conn.close()
#             return redirect(url_for("add_expense"))

#         # ---- INSERT EXPENSE ----
#         cursor.execute(
#             """
#             INSERT INTO expenses (user_id, date, category, amount, description)
#             VALUES (?, ?, ?, ?, ?)
#             """,
#             (session["user_id"], date_input, category, amount, description)
#         )

#         conn.commit()
#         conn.close()

#         flash("Expense added successfully!", "success")
#         return redirect(url_for("dashboard"))

#     # ---- GET REQUEST ----
#     return render_template(
#         "expense_form.html",
#         categories=EXPENSE_CATEGORIES,
#         current_date=date.today().strftime("%Y-%m-%d"),
#         mode="add"
#     )



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


# ---- Edit Income ----

# @app.route("/edit_income/<int:income_id>", methods=["GET","POST"])
# def edit_income(income_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]
        cursor.execute(
            "UPDATE income SET category=?, amount=?, description=? WHERE id=? AND user_id=?",
            (category, amount, description, income_id, session["user_id"])
        )
        conn.commit()
        conn.close()
        flash("Income updated successfully!", "success")
        return redirect(url_for("dashboard"))
    cursor.execute("SELECT category, amount, description FROM income WHERE id=? AND user_id=?",
                   (income_id, session["user_id"]))
    record = cursor.fetchone()
    conn.close()
    if not record:
        flash("Record not found!", "danger")
        return redirect(url_for("dashboard"))
    return render_template("edit_income.html", categories=INCOME_CATEGORIES, record=record)

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
# @app.route("/edit_expense/<int:expense_id>", methods=["GET","POST"])
# def edit_expense(expense_id):
#     if "user_id" not in session:
#         return redirect(url_for("login"))
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     if request.method == "POST":
#         category = request.form["category"]
#         amount = float(request.form["amount"])
#         description = request.form["description"]

#         # Check available balance excluding this expense
#         cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
#         total_income = cursor.fetchone()[0] or 0
#         cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND id<>?", (session["user_id"], expense_id))
#         total_expense_except_current = cursor.fetchone()[0] or 0
#         available_balance = total_income - total_expense_except_current
#         if amount > available_balance:
#             flash(f"Expense exceeds available balance ({available_balance})!", "danger")
#             conn.close()
#             return redirect(url_for("edit_expense", expense_id=expense_id))

#         cursor.execute(
#             "UPDATE expenses SET category=?, amount=?, description=? WHERE id=? AND user_id=?",
#             (category, amount, description, expense_id, session["user_id"])
#         )
#         conn.commit()
#         conn.close()
#         flash("Expense updated successfully!", "success")
#         return redirect(url_for("dashboard"))

#     cursor.execute("SELECT category, amount, description FROM expenses WHERE id=? AND user_id=?",
#                    (expense_id, session["user_id"]))
#     record = cursor.fetchone()
#     conn.close()
#     if not record:
#         flash("Record not found!", "danger")
#         return redirect(url_for("dashboard"))
#     return render_template("edit_expense.html", categories=EXPENSE_CATEGORIES, record=record)

@app.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]

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
            return redirect(
                url_for("edit_expense", expense_id=expense_id)
            )

        # ---- UPDATE EXPENSE ----
        cursor.execute(
            """
            UPDATE expenses
            SET category=?, amount=?, description=?
            WHERE id=? AND user_id=?
            """,
            (category, amount, description, expense_id, session["user_id"])
        )

        conn.commit()
        conn.close()

        flash("Expense updated successfully!", "success")
        return redirect(url_for("dashboard"))

    # ---- GET REQUEST (LOAD RECORD) ----
    cursor.execute(
        """
        SELECT category, amount, description
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
# @app.route("/charts")
# def charts():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     # Income grouped by category
#     cursor.execute("""
#         SELECT category, SUM(amount)
#         FROM income
#         WHERE user_id=?
#         GROUP BY category
#     """, (session["user_id"],))
#     income_data = cursor.fetchall()

#     # Expense grouped by category
#     cursor.execute("""
#         SELECT category, SUM(amount)
#         FROM expenses
#         WHERE user_id=?
#         GROUP BY category
#     """, (session["user_id"],))
#     expense_data = cursor.fetchall()

#     conn.close()

#     income_labels = [row[0] for row in income_data]
#     income_values = [row[1] for row in income_data]

#     expense_labels = [row[0] for row in expense_data]
#     expense_values = [row[1] for row in expense_data]

#     return render_template(
#         "charts.html",
#         income_labels=income_labels,
#         income_values=income_values,
#         expense_labels=expense_labels,
#         expense_values=expense_values
#     )
@app.route("/charts", methods=["GET", "POST"])
def charts():
    if "user_id" not in session:
        return redirect(url_for("login"))

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
        end_date=end_date
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

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        total_income=total_income,
        total_expense=total_expense
    )


# edit profile 
# ===============================
# @app.route("/update-profile", methods=["POST"])
# def update_profile():

#     if "username" not in session:
#         return redirect(url_for("login"))

#     username_session = session["username"]

#     new_username = request.form["username"].strip()
#     new_password = request.form.get("password")
#     avatar_file = request.files.get("avatar")

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     # Get existing avatar
#     cursor.execute(
#         "SELECT avatar FROM users WHERE username = ?",
#         (username_session,)
#     )
#     old_avatar = cursor.fetchone()[0]

#     avatar_name = old_avatar

#     # -----------------------
#     # Username conflict check
#     # -----------------------
#     cursor.execute(
#         "SELECT id FROM users WHERE username = ? AND username != ?",
#         (new_username, username_session)
#     )
#     if cursor.fetchone():
#         flash("Username already exists", "danger")
#         return redirect(url_for("edit_profile"))

#     # -----------------------
#     # Avatar Upload
#     # -----------------------
#     if avatar_file and avatar_file.filename != "":
#         filename = secure_filename(avatar_file.filename)
#         avatar_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
#         avatar_name = filename

#     # -----------------------
#     # Update logic
#     # -----------------------
#     if new_password:
#         hashed_pw = generate_password_hash(new_password)
#         cursor.execute(
#             """
#             UPDATE users
#             SET username=?, password=?, avatar=?
#             WHERE username=?
#             """,
#             (new_username, hashed_pw, avatar_name, username_session)
#         )
#     else:
#         cursor.execute(
#             """
#             UPDATE users
#             SET username=?, avatar=?
#             WHERE username=?
#             """,
#             (new_username, avatar_name, username_session)
#         )

#     conn.commit()
#     conn.close()

#     # Update session
#     session["username"] = new_username
#     session["avatar"] = avatar_name

#     flash("Profile updated successfully", "success")
#     return redirect(url_for("dashboard"))

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True)

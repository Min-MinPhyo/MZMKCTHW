from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_NAME = "database.db"

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
        password TEXT NOT NULL
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
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(username,password) VALUES(?,?)", (username,password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")
    return render_template("register.html")

# ---- Login ----
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")
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
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]
        date_input = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # ---- BALANCE CHECK ----
        cursor.execute(
            "SELECT SUM(amount) FROM income WHERE user_id=?",
            (session["user_id"],)
        )
        total_income = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id=?",
            (session["user_id"],)
        )
        total_expense = cursor.fetchone()[0] or 0

        available_balance = total_income - total_expense

        if total_income == 0:
            flash("Add income first!", "danger")
            conn.close()
            return redirect(url_for("add_expense"))

        if amount > available_balance:
            flash(
                f"Expense exceeds available balance ({available_balance})!",
                "danger"
            )
            conn.close()
            return redirect(url_for("add_expense"))

        # ---- INSERT EXPENSE ----
        cursor.execute(
            """
            INSERT INTO expenses (user_id, date, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session["user_id"], date_input, category, amount, description)
        )

        conn.commit()
        conn.close()

        flash("Expense added successfully!", "success")
        return redirect(url_for("dashboard"))

    # ---- GET REQUEST ----
    return render_template(
        "expense_form.html",
        categories=EXPENSE_CATEGORIES,
        current_date=date.today().strftime("%Y-%m-%d"),
        mode="add"
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

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True)

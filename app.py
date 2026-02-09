from flask import Flask, render_template, request, redirect, url_for, session, flash
import string
import smtplib # Error အမျိုးအစား ခွဲခြားရန် လိုအပ်သည်
import sqlite3
from datetime import datetime, date
import os
import re
import random

import time
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


# google translate for en/mm version
from googletrans import Translator


# mail testing and reset password 
from flask_mail import Mail, Message

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

# 
import os

if __name__ == "__main__":
    import os
    # PORT ကို Environment ကနေ ယူမယ်၊ မရှိရင် 5000 ကို သုံးမယ်
    port = int(os.environ.get("PORT", 5000))
    # host ကို '0.0.0.0' ပေးမှသာ Render က အပြင်ကို ပေးထွက်မှာပါ
    app.run(host='0.0.0.0', port=port)
    
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')

def get_db_connection():
    # 20 seconds ထိ စောင့်ခိုင်းထားတာ ဖြစ်ပါတယ် (ပုံမှန်က 5 seconds ပဲရှိလို့ Lock ခဏခဏ ဖြစ်တာပါ)
    conn = sqlite3.connect(db_path, timeout=20) 
    conn.row_factory = sqlite3.Row
    return conn

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


# languages 
# ================= LANGUAGE DICTIONARY =================
LANGUAGES = {
    "en": {
        # ===== App =====
        "app_title": "Expense Tracker",
        "dashboard": "Income & Expense Dashboard",
        "welcome":"Welcome back",
        "savings_goals":"Saving Goal",
        "forgot_password_title":"Forgot Password",
        "update_success":"Expense Updated Successful",

        # ===== General =====
        "welcome": "Welcome back",
        "login_success": "Login successful!",
        "logout_success": "Logged out!",
        "register_success": "Registration successful! Please login.",
        "user_exists_error":"This user already is already exit",
        "password_policy_error":"Password must be at least 6 characters",
        
        # register requirement
        "register_title": "Create Account",
        "register_subtitle": "Start tracking your income & expenses 💰",
        "username": "Username",
        "username_placeholder": "Enter your username",
        "email": "Email",
        "email_placeholder": "example@email.com",
        "email_address":"Email Address",
        "password": "Password",
        "password_placeholder": "Minimum 6 characters and special character",
        "register_btn": "Register",
        "already_account": "Already have an account?",
        "login_here": "Login here",
        
        # login for requirement 
         "login_title": "Login to Your Business Account",
        "username": "Username",
        "username_placeholder": "Enter your username",
        "password": "Password",
        "password_placeholder": "Enter your password",
        "avatar_upload": "Update Profile Image (optional)",
        "login": "Login",
        "no_account": "Don't have an account?",
        "register": "Register",
        "login_footer": "By logging in, you agree to our",
        "terms": "Terms & Conditions",
        "forgot_password":"Forgot Password",

        # ===== Income / Expense =====
        "income_added": "Income added successfully!",
        "expense_added": "Expense added successfully!",
        "income_deleted": "Income deleted!",
        "income_updated": "Income updated successfully!",
        "exceed_balance": "Expense exceeds available balance",
        "confirm_all_balance": "This expense will use ALL your remaining balance. Please confirm.",

        # ===== Categories =====
        "Salary": "Salary",
        "Business": "Business",
        "Food & Dining": "Food & Dining",
        "Transportation": "Transportation",
        "Others": "Others",

        # ===== Dashboard UI =====
        "start_date": "Start Date",
        "end_date": "End Date",
        "apply": "Apply",
        "reset_filter": "Reset Filter",
        "quick_filter": "Quick Filter",
        "all": "All",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "yearly": "Yearly",
        "total_income": "Total Income",
        "total_expense": "Total Expense",
        "balance": "Balance",
        "add_income": "Add Income",
        "add_expense": "Add Expense",
        "charts": "Charts",
        "pdf_report": "PDF Report",
        "play_quiz": "🧠 Play Quiz",
        "no_records": "No records found",
        "edit": "Edit",
        "delete": "Delete",
        "delete_confirm": "Delete this record?",
        "description": "Description",
        "category": "Category",
        "amount": "Amount",
        "date": "Date",
        "all_fields_required":"All Fields are required",
        # pagination
        "prev_pagination":"Prev",
        "next_pagination":"Next",
        
        # action
        "action":"Action",
        
        # income add/edit requirement
        "add_income_title": "Add Income",
        "edit_income_title": "Edit Income",
        "date": "Date",
        "category": "Category",
        "select_category": "Select Category",
        "amount": "Amount",
        "amount_placeholder": "Enter amount",
        "description": "Description",
        "description_placeholder": "Enter description",
        "description_hint": "Maximum 100 characters",
        "update_income_btn": "Update Income",
        "add_income_btn": "Add Income",
        "back_dashboard": "Back to Dashboard",
        
        # Expense form requirement
        "add_expense_title": "Add Expense",
        "edit_expense_title": "Edit Expense",
        "date": "Date",
        "category": "Category",
        "select_category": "Select Category",
        "amount": "Amount",
        "amount_placeholder": "Enter amount",
        "description": "Description",
        "description_placeholder": "Optional note",
        "update_expense_btn": "Update Expense",
        "add_expense_btn": "Add Expense",
        "back_dashboard": "Back to Dashboard",

        # ===== Warning / Confirm =====
         "expense_warning": "Warning: This will use all your remaining balance.",
         "confirm_continue": "Yes, I understand and want to continue",

        # Category keys (already DB-safe)
        "Salary": "Salary",
        "Business": "Business",
        "Food & Dining": "Food & Dining",
        "Transportation": "Transportation",
        "Others": "Others",
        
         # ===== Income Categories =====
        "Salary": "Salary",
        "Business": "Business",
        "Investments": "Investments",
        "Rental Income": "Rental Income",
        "Gifts": "Gifts",
        "Bonuses": "Bonuses",
        "Refunds": "Refunds",
        "Other": "Other",

        # ===== Expense Categories =====
        "Food & Dining": "Food & Dining",
        "Rent / Housing": "Rent / Housing",
        "Transportation": "Transportation",
        "Health & Medical": "Health & Medical",
        "Entertainment": "Entertainment",
        "Education": "Education",
        "Shopping": "Shopping",
        "Travel": "Travel",
        "Utilities": "Utilities",
        "Insurance": "Insurance",
        "Taxes": "Taxes",
        "Others": "Others",
        
        # ===== Charts / Analysis =====
        "analysis_title": "Income & Expense Analysis",
        "analysis_subtitle": "Visualize your financial activity by category",

        "start_date": "Start Date",
        "end_date": "End Date",
        "filter": "Filter",
        "reset": "Reset",

        "income_by_category": "Income by Category",
        "expense_by_category": "Expense by Category",

        "total_income": "Total Income",
        "total_expense": "Total Expense",
        "balance": "Balance",

        "back_dashboard": "Back to Dashboard",
        "amount_mmk": "Amount",
        
        
        # Tables
        "records_table": "Records",
        "date": "Date",
        "category": "Category",
        "amount": "Amount",
        "description": "Description",
        "actions": "Actions",
        "edit": "Edit",
        "delete": "Delete",
        "no_data": "No records found",

        "income": "Income",
        "expense": "Expense",

        "prev": "Previous",
        "next": "Next",
        
        # profile
        "user_profile":"My Profile",
        "edit_profile":"Edit Profile",
        "cancel_edit":"Home",
        
        # updated profile
        "old_password":"Old",
        "new_password":"New Password",
        "update_btn":"Update Profile",
        "leave_blank_to_keep":"enter match old password",
        
        
        
        # Quiz Result Keys
        "quiz_result_title": "🏁 Quiz Result",
        "quiz_result_subtitle": "See how well you did!",
        "quiz_excellent": "Excellent! Perfect Score!",
        "quiz_good": "Good job! Keep going!",
        "quiz_keep_trying": "Keep practicing! You’ll improve!",
        "accuracy": "Accuracy",
        "play_again": "Play Again",
        "back_dashboard": "Dashboard",
        "next": "Next Question",
        "play_quiz": "🧠 Quiz Game",
        "records": "Question",
        "cancel": "Quit Quiz",
        "reset": "Restart Quiz",
        "edit_profile_title":"Edit Profile",
        
        
        # Saving goals
        "title": "Savings Goals 🎯",
        "subtitle": "Plan your future and track your progress.",
        "dashboard": "Dashboard",
        "createNew": "Create New Goal",
        "goalName": "Goal Name",
        "placeholderName": "e.g. New Laptop",
        "targetAmount": "Target (MMK)",
        "setGoal": "SET SAVINGS GOAL",
        "targetLabel": "Target",
        "progress": "Progress",
        "saved": "saved",
        "updateLabel": "Update Current Savings",
        "updateBtn": "UPDATE",
        "noGoals": "No savings goals yet. Start dreaming!",
        "deleteConfirm": "Are you sure you want to delete this goal?",
        
        "reset_chart":"Reset Data",
        "income_success":"Income Successfully Data",
        "expense_success":"Expense Successfully Data",
        

    },

    "mm": {
        # ===== App =====
        "app_title": "ငွေထွက်ထိန်းခြင်း",
        "dashboard": "ဝင်ငွေနှင့် ကုန်ကျစရိတ် ဒက်ရှ်ဘုတ်",
        "welcome":"အားလုံးကို ကြိုဆိုပါတယ် ချစ်တို့ရေ",
        "savings_goals":"ငွေစုဆောင်းရည်မှန်းချက်",
        "all_fields_required":"အချက်အလက်အားလုံး ဖြည့်စွက်ရန် လိုအပ်သည်",
        "update_success":"အသုံးစရိတ် ပြင်ဆင်မှု အောင်မြင်ပါသည်",
         "income_success":"ဝင်ငွေအချက်အလက်များကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ",
         "expense_success":"အသုံးစရိတ်အချက်အလက်များကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ",
          "user_exists_error":"ဤအသုံးပြုသူအမည်ဖြင့် အကောင့်ရှိပြီးသားဖြစ်သည်",
          "password_policy_error":"လျှို့ဝှက်နံပါတ်သည် အနည်းဆုံး စာလုံး (၆) လုံး ရှိရပါမည်",
        # ===== General =====
        "welcome": "ပြန်လည်ကြိုဆိုပါတယ်",
        "login":"ဝင်ရောက်မှု",
        "login_success": "ဝင်ရောက်မှု အောင်မြင်ပါသည်",
        "logout":"ထွက်လိုက်ပါ",
        "logout_success": "ထွက်ပြီးပါပြီ",
        "register_success": "စာရင်းသွင်းမှု အောင်မြင်ပါသည်",
        # ===== Income / Expense =====
        "income_added": "ဝင်ငွေ ထည့်ပြီးပါပြီ",
        "expense_added": "အသုံးစရိတ် ထည့်ပြီးပါပြီ",
        "income_deleted": "ဝင်ငွေ ဖျက်ပြီးပါပြီ",
        "income_updated": "ဝင်ငွေ ပြင်ဆင်ပြီးပါပြီ",
        "exceed_balance": "လက်ကျန်ငွေထက် ပိုများနေပါသည်",
        "confirm_all_balance": "လက်ကျန်ငွေအားလုံး သုံးမည်ဖြစ်ပါသည်။ အတည်ပြုပါ။",
        "email_address":"အီးမေးလ် လိပ်စာ",
        # ===== Categories =====
        "Salary": "လစာ",
        "Business": "လုပ်ငန်း",
        "Food & Dining": "အစားအစာ",
        "Transportation": "သယ်ယူပို့ဆောင်ရေး",
        "Others": "အခြား",
        # ===== Dashboard UI =====
        "start_date": "စတင်နေ့စွဲ",
        "end_date": "ပြီးဆုံးနေ့စွဲ",
        "apply": "လျှောက်ထားမည်",
        "reset_filter": "ပြန်သတ်မှတ်မည်",
        "quick_filter": "အမြန်စစ်ထုတ်ရန်",
        "all": "အားလုံး",
        "weekly": "အပတ်စဉ်",
        "monthly": "လစဉ်",
        "yearly": "နှစ်စဉ်",
        "total_income": "စုစုပေါင်း ဝင်ငွေ",
        "total_expense": "စုစုပေါင်း အသုံးစရိတ်",
        "balance": "လက်ကျန်ငွေ",
        "add_income": "ဝင်ငွေ ထည့်မည်",
        "add_expense": "အသုံးစရိတ် ထည့်မည်",
        "charts": "ဇယားများ",
        "pdf_report": "PDF အစီရင်ခံစာ",
        "play_quiz": "🧠 စမ်းသပ်မည်",
        "no_records": "မှတ်တမ်း မရှိပါ",
        "edit": "ပြင်မည်",
        "delete": "ဖျက်မည်",
        "delete_confirm": "ဤ မှတ်တမ်းကို ဖျက်မည်လား?",
        "description": "ဖော်ပြချက်",
        "category": "အမျိုးအစား",
        "amount": "ငွေပမာဏ",
        "date": "နေ့စွဲ",
        "reset_chart":"အချက်အလက်အားလုံးကို ဖျက်ပစ်ခြင်း",
        # register requirement
         "register_title": "အကောင့်အသစ်ဖန်တီးရန်",
        "register_subtitle": "သင်၏ဝင်ငွေ နှင့် အသုံးစရိတ်ကို စတင်စောင့်ကြည့်ပါ 💰",
        "username": "အသုံးပြုသူအမည်",
        "username_placeholder": "သင့်အသုံးပြုသူအမည် ထည့်ပါ",
        "email": "အီးမေးလ်",
        "email_placeholder": "ဥပမာ@email.com",
        "password": "စကားဝှက်",
        "password_placeholder": "အနည်းဆုံး ၆ လုံးနှင့် အထူးအက္ခရာပါဝင်ရမည်",
        "register_btn": "စာရင်းသွင်းမည်",
        "already_account": "အကောင့်ရှိပြီးပါသလား?",
        "login_here": "ဒီမှာဝင်ပါ",
        # login requirement
        "login_title": "သင့်စီးပွားရေးအကောင့်သို့ ဝင်ရန်",
        "username": "အသုံးပြုသူအမည်",
        "username_placeholder": "သင့်အသုံးပြုသူအမည်ထည့်ပါ",
        "password": "စကားဝှက်",
        "password_placeholder": "သင့်စကားဝှက်ထည့်ပါ",
        "avatar_upload": "ပရိုဖိုင်ပုံထည့်ရန် (လိုအပ်လျှင်)",
        "login": "ဝင်မည်",
        "no_account": "အကောင့်မရှိသေးပါက",
        "register": "စာရင်းသွင်းပါ",
        "login_footer": "ဝင်ရောက်ခြင်းဖြင့်၊ သင်သည် ကျွန်ုပ်တို့၏",
        "terms": "စည်းမျဉ်းနှင့်စည်းမျဉ်းများ",
        "forgot_password":"စကားဝှက်မေ့နေပါသလား",
        # pagination
        "prev_pagination":"ယခင်",
        "next_pagination":"နောက်တစ်ခု",
        # Action
        "action":"လုပ်ဆောင်ချက်များ",
        # income add/edit requirement
        "add_income_title": "ဝင်ငွေ ထည့်ရန်",
        "edit_income_title":"ဝင်ငွေကို တည်းဖြတ်ပါ",
        "date": "ရက်စွဲ",
        "category": "အမျိုးအစား",
        "select_category": "အမျိုးအစား ရွေးပါ",
        "amount": "ပမာဏ",
        "amount_placeholder": "ငွေပမာဏ ထည့်ပါ",
        "description": "ဖော်ပြချက်",
        "description_placeholder": "ဖော်ပြချက် ထည့်ပါ",
        "description_hint": "စာလုံး ၁၀၀ အထိသာ ရပါသည်",
        "add_income_btn": "ဝင်ငွေ ထည့်မည်",
        "update_income_btn":"ဝင်ငွေကို အပ်ဒိတ်လုပ်ပါ",
        "back_dashboard": "ဒက်ရှ်ဘုတ်သို့ ပြန်သွားရန်",
        # expense form requirement
        "add_expense_title": "အသုံးစရိတ် ထည့်ရန်",
        "edit_expense_title": "အသုံးစရိတ် ပြင်ဆင်ရန်",
        "date": "ရက်စွဲ",
        "category": "အမျိုးအစား",
        "select_category": "အမျိုးအစား ရွေးပါ",
        "amount": "ပမာဏ",
        "amount_placeholder": "ငွေပမာဏ ထည့်ပါ",
        "description": "ဖော်ပြချက်",
        "description_placeholder": "မှတ်ချက် (မဖြစ်မနေ မလို)",
        "update_expense_btn": "ပြင်ဆင်မည်",
        "add_expense_btn": "ထည့်မည်",
        "back_dashboard": "ဒက်ရှ်ဘုတ်သို့ ပြန်သွားရန်",

        "expense_warning": "လက်ကျန်ငွေအားလုံး အသုံးပြုမည် ဖြစ်ပါသည်။",
        "confirm_continue": "နားလည်ပါသည်၊ ဆက်လုပ်ပါမည်",
        "forgot_password_title":"စကားဝှက် ပြန်လည်သတ်မှတ်ရန်",
        # Category translations
        "Salary": "လစာ",
        "Business": "လုပ်ငန်း",
        "Food & Dining": "အစားအသောက်",
        "Transportation": "သယ်ယူပို့ဆောင်ရေး",
        "Others": "အခြား",
          # ===== Income Categories =====
        "Salary": "လစာ",
        "Business": "လုပ်ငန်း",
        "Investments": "ရင်းနှီးမြှုပ်နှံမှု",
        "Rental Income": "အိမ်ခြံမြေ ငှားရမ်း ဝင်ငွေ",
        "Gifts": "လက်ဆောင်ငွေ",
        "Bonuses": "ဆုကြေးငွေ",
        "Refunds": "ပြန်လည်ရရှိငွေ",
        "Other": "အခြား",
        # ===== Expense Categories =====
        "Food & Dining": "အစားအသောက်",
        "Rent / Housing": "အိမ်လခ / နေအိမ်",
        "Transportation": "သယ်ယူပို့ဆောင်ရေး",
        "Health & Medical": "ကျန်းမာရေး / ဆေးကုသမှု",
        "Entertainment": "ဖျော်ဖြေရေး",
        "Education": "ပညာရေး",
        "Shopping": "စျေးဝယ်ခြင်း",
        "Travel": "ခရီးသွားလာရေး",
        "Utilities": "မီး / ရေ / အင်တာနက်",
        "Insurance": "အာမခံ",
        "Taxes": "အခွန်",
        "Others": "အခြား",
        # ===== Charts / Analysis =====
        "analysis_title": "ဝင်ငွေ / အသုံးစရိတ် ခွဲခြမ်းစိတ်ဖြာခြင်း",
        "analysis_subtitle": "အမျိုးအစားအလိုက် သင့်ငွေစာရင်းကို ကြည့်ရှုပါ",
        "start_date": "အစ ရက်စွဲ",
        "end_date": "အဆုံး ရက်စွဲ",
        "filter": "စစ်ထုတ်မည်",
        "reset": "ပြန်လည်သတ်မှတ်မည်",
        "income_by_category": "အမျိုးအစားအလိုက် ဝင်ငွေ",
        "expense_by_category": "အမျိုးအစားအလိုက် အသုံးစရိတ်",
        "total_income": "စုစုပေါင်း ဝင်ငွေ",
        "total_expense": "စုစုပေါင်း အသုံးစရိတ်",
        "balance": "လက်ကျန်ငွေ",
        "back_dashboard": "ဒက်ရှ်ဘုတ်သို့ ပြန်သွားရန်",
        "amount_mmk": "ငွေပမာဏ",
        #Tables
        "records_table": "မှတ်တမ်းများ",
        "date": "ရက်စွဲ",
        "category": "အမျိုးအစား",
        "amount": "ပမာဏ",
        "description": "ဖော်ပြချက်",
        "actions": "လုပ်ဆောင်ချက်များ",
        "edit": "ပြင်ဆင်",
        "delete": "ဖျက်ရန်",
        "no_data": "မှတ်တမ်း မရှိပါ",
        "income": "ဝင်ငွေ",
        "expense": "အသုံးစရိတ်",
        "prev": "နောက်သို့",
        "next": "ရှေ့သို့",      
        # profile
        "user_profile":"အသုံးပြုသူပရိုဖိုင်",
        "edit_profile_title":"Profile ကို တည်းဖြတ်ပါ",
        "cancel_edit":"ပင်မစာမျက်နှာ",
        # update profile
        "old_password":"စကားဝှက်အဟောင်း",
        "new_password":"စကားဝှက်အသစ်",
        "update_btn":"စကားဝှက်ကို အပ်ဒိတ်",
        "leave_blank_to_keep":"စကားဝှက်ဟောင်းနှင့် ကိုက်ညီသော စကားဝှက်အသစ်ကို ရိုက်ထည့်ပါ",
        # Quiz Result Keys (မြန်မာဘာသာ)
        "quiz_result_title": "🏁 ဖြေဆိုမှုရလဒ်",
        "quiz_result_subtitle": "သင်ဘယ်လောက်ထိ တော်သလဲဆိုတာ ကြည့်လိုက်ပါဦး!",
        "quiz_excellent": "ထူးချွန်ပါတယ်! အမှတ်ပြည့်ရပါတယ်!",
        "quiz_good": "တော်ပါတယ်! ဒီထက်မက ကြိုးစားပါဦး!",
        "quiz_keep_trying": "ထပ်ပြီးလေ့ကျင့်ပါဦး! မကြာခင် တိုးတက်လာမှာပါ!",
        "accuracy": "မှန်ကန်မှုနှုန်း",
        "play_again": "ပြန်ဖြေမယ်",
        "back_dashboard": "ပင်မစာမျက်နှာ",
        "next": "နောက်တစ်ပုဒ်",
        "play_quiz": "🧠 ဉာဏ်စမ်းပဟေဠိ",
        "records": "မေးခွန်းနံပါတ်",
        "cancel": "ထွက်မည်",
        "reset": "အစကပြန်စမည်",
        # Saving goals
        "title": "စုငွေရည်မှန်းချက်များ 🎯",
        "subtitle": "သင့်အနာဂတ်အတွက် စနစ်တကျ စုဆောင်းပါ။",
        "dashboard": "ပင်မစာမျက်နှာ",
        "createNew": "ရည်မှန်းချက်အသစ်ပြုလုပ်ရန်",
        "goalName": "အမည်",
        "placeholderName": "ဥပမာ - ကွန်ပျူတာအသစ်",
        "targetAmount": "ရည်မှန်းချက်ပမာဏ (ကျပ်)",
        "setGoal": "ရည်မှန်းချက်သတ်မှတ်မည်",
        "targetLabel": "ပမာဏ",
        "progress": "တိုးတက်မှု",
        "saved": "စုဆောင်းပြီး",
        "updateLabel": "စုဆောင်းမိသော ပမာဏကိုပြင်ရန်",
        "updateBtn": "ပြင်ဆင်မည်",
        "noGoals": "ရည်မှန်းချက် မရှိသေးပါ။ အခုပဲ စတင်လိုက်ပါ။",
        "deleteConfirm": "ဤရည်မှန်းချက်ကို ဖျက်ရန် သေချာပါသလား?"
    }
}


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
    
    # Savings Goals Table အသစ်
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            target_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()
# ---- Home ----
@app.route("/")
def index():
    return redirect(url_for("login"))

# test register updated
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
@app.route("/register", methods=["GET", "POST"])
def register():
    form_data = {}
    if request.method == "POST":
        form_data = request.form
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        avatar_file = request.files.get("avatar")
        if not username or not email or not password:
            flash(t("all_fields_required"), "danger")
            return render_template("register.html", form_data=form_data)

        if not EMAIL_REGEX.match(email):
            flash(t("invalid_email"), "danger")
            return render_template("register.html", form_data=form_data)
        if not re.match(r"^(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{6,}$", password):
            flash(t("password_policy_error"), "danger")
            return render_template("register.html", form_data=form_data)
        avatar_filename = "default_avatar.png"  
        if avatar_file and avatar_file.filename != '':
            if allowed_file(avatar_file.filename):
                ext = avatar_file.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"{username}_{avatar_file.filename}")
                avatar_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                avatar_filename = filename
            else:
                flash(t("invalid_file_format"), "danger")
                return render_template("register.html", form_data=form_data)

        try:
            hashed_password = generate_password_hash(password)
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users(username, email, password, avatar) VALUES (?, ?, ?, ?)",
                (username, email, hashed_password, avatar_filename)
            )
            
            conn.commit()
            conn.close()

            flash(t("register_success"), "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash(t("user_exists_error"), "danger")
            return render_template("register.html", form_data=form_data)
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return render_template("register.html", form_data=form_data)

    return render_template("register.html", form_data={})

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
        filename = user["avatar"] 

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

# ---- Logout ---
@app.route("/logout")
def logout():
    # Clear the session
    session.clear()
    lang = session.get("lang", "en")
    flash(LANGUAGES.get(lang, LANGUAGES["en"]).get("logout_success", "Logged out!"), "success")
    return redirect(url_for("login"))
# saving goal testing dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    #Filter & Pagination Parameters ---
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    filter_type = request.args.get("filter")
    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.today()
    this_month = today.strftime('%Y-%m')
    last_month = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
    
    # Fast Filter Logic
    if filter_type == "weekly":
        start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif filter_type == "monthly":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif filter_type == "yearly":
        start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        #start date is not greater than end date 
    if start_date and end_date:
        # String ကနေ Date Object ပြောင်းလဲခြင်း
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Condition: Start date က End date ထက် ကြီးနေပါက
        if start_date > end_date:
            # Error Message ပြသခြင်း (Option)
            flash("စတင်သည့်ရက်စွဲသည် ပြီးဆုံးသည့်ရက်စွဲထက်မကြီးရပါ။", "error")
            return redirect(request.referrer) # သို့မဟုတ် သင့်တော်ရာ Page သို့ပြန်လွှတ်ပါ 

    # ဒီလအတွက် ဝင်ငွေ/ထွက်ငွေ (Saving Rate အတွက်)
    cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=? AND strftime('%Y-%m', date)=?", (user_id, this_month))
    this_month_income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?", (user_id, this_month))
    this_month_expense = cursor.fetchone()[0] or 0


    # ပြီးခဲ့တဲ့လအတွက် ထွက်ငွေ (Comparison အတွက်)
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?", (user_id, last_month))
    last_month_expense = cursor.fetchone()[0] or 0
    # ၁။ Saving Rate တွက်ချက်ခြင်း
    if this_month_income > 0:
       # ပထမဦးစွာ ရာခိုင်နှုန်းကို တွက်ပါ
        calculated_rate = ((this_month_income - this_month_expense) / this_month_income) * 100
        
        # min() ထဲမှာ တွက်လို့ရတဲ့နှုန်း နဲ့ 100 ကို နှိုင်းယှဉ်ပြီး အနည်းဆုံးကို ယူပါ
        # ပြီးမှ round() နဲ့ ဒသမ ၁ နေရာ ဖြတ်ပါ
        saving_rate = round(min(calculated_rate, 100), 1)
       
    else:
        saving_rate = 0
        
        
        # --- ၆။ Savings Goals Summary ---
    # စုစုပေါင်း စုမိငွေ (Total Amount Saved in Goals)
    cursor.execute("SELECT SUM(current_amount) FROM savings_goals WHERE user_id=?", (user_id,))
    total_saved_in_goals = cursor.fetchone()[0] or 0

    # Goal တစ်ခုချင်းစီရဲ့ အချက်အလက်များကို ဆွဲထုတ်ခြင်း
    cursor.execute("SELECT id, goal_name, target_amount, current_amount FROM savings_goals WHERE user_id=?", (user_id,))
    currentgoals = cursor.fetchall()    


 # expense comparison testing
# Intent: ဒီလ ဘာမှမသုံးရင် 0% ပြရန်၊ အရင်လနှင့်နှိုင်းယှဉ်၍ 100% ထက်မကျော်သော Realistic Data ပြရန်။
    if this_month_expense == 0:
        # ဒီလမှာ အသုံးစရိတ် တစ်ပြားမှ မရှိသေးရင် အမြဲတမ်း 0% ပဲ ပြမယ်
        diff_percent = 0.0

    elif last_month_expense > 0:
        # အရင်လက အသုံးစရိတ် ရှိခဲ့ရင် ပုံမှန် Percent တွက်နည်းကို သုံးမယ်
        raw_diff = ((this_month_expense - last_month_expense) / last_month_expense) * 100
        
        if raw_diff > 0:
            # အသုံးစရိတ် တိုးလာတဲ့အခါမှာ အများဆုံး 100% မှာပဲ ကန့်သတ် (Cap) မယ်
            diff_percent = min(round(raw_diff, 1), 100.0)
        else:
            # အသုံးစရိတ် လျော့သွားရင်တော့ (အနှုတ်တန်ဖိုးကို) အရှိအတိုင်း ပြမယ်
            diff_percent = round(raw_diff, 1)

    else:
        # အရင်လက အသုံးစရိတ် (၀) ဖြစ်နေပြီး ဒီလမှာ စသုံးလာတဲ့ အခြေအနေ
        if this_month_income > 0:
            # ဝင်ငွေရှိရင် ဝင်ငွေနဲ့ နှိုင်းယှဉ်ပြီး သင့်လျော်တဲ့ Growth ကို တွက်မယ်
            relative_usage = (this_month_expense / this_month_income) * 100
            diff_percent = min(round(relative_usage, 1), 100.0)
        else:
            # ဝင်ငွေရော အရင်လစရိတ်ရော မရှိဘဲ သုံးနေရင်တော့ အမြင့်ဆုံး 100% လို့ သတ်မှတ်မယ်
            diff_percent = 100.0
    
        
 

    # --- ၃။ Total Summaries (With Date Filtering) ---
    income_sum_query = "SELECT SUM(amount) FROM income WHERE user_id=?"
    expense_sum_query = "SELECT SUM(amount) FROM expenses WHERE user_id=?"
    base_params = [user_id]
    filter_params = []

    if start_date and end_date:
        income_sum_query += " AND date BETWEEN ? AND ?"
        expense_sum_query += " AND date BETWEEN ? AND ?"
        filter_params = [start_date, end_date]

    cursor.execute(income_sum_query, base_params + filter_params)
    total_income = cursor.fetchone()[0] or 0
    cursor.execute(expense_sum_query, base_params + filter_params)
    total_expense = cursor.fetchone()[0] or 0
    balance = total_income - total_expense

    # --- ၄။ Fetch Records (Income & Expenses) ---
    # Income Records
    inc_select = "SELECT id, category, amount, date, description FROM income WHERE user_id=?"
    if start_date and end_date:
        inc_select += " AND date BETWEEN ? AND ?"
    inc_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
    cursor.execute(inc_select, base_params + filter_params + [per_page, offset])
    income_records = cursor.fetchall()

    # Expense Records
    exp_select = "SELECT id, category, amount, date, description FROM expenses WHERE user_id=?"
    if start_date and end_date:
        exp_select += " AND date BETWEEN ? AND ?"
    exp_select += " ORDER BY date DESC LIMIT ? OFFSET ?"
    cursor.execute(exp_select, base_params + filter_params + [per_page, offset])
    expense_records = cursor.fetchall()

    # --- ၅။ Pagination Counts ---
    cursor.execute("SELECT COUNT(*) FROM income WHERE user_id=?", (user_id,))
    total_income_pages = (cursor.fetchone()[0] + per_page - 1) // per_page
    cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id=?", (user_id,))
    total_expense_pages = (cursor.fetchone()[0] + per_page - 1) // per_page

    # --- ၆။ Savings Goals ---
    
    cursor.execute("SELECT id, user_id, goal_name, target_amount, current_amount FROM savings_goals WHERE user_id=?", (user_id,))
    goals = cursor.fetchall()

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
        filter_type=filter_type,
        saving_rate=saving_rate,
        diff_percent=diff_percent,
        this_month_expense=this_month_expense,
        goals=goals,
        currentgoals=currentgoals
    )
    
    

    
    
#savings goals
@app.route("/savings", methods=["GET", "POST"])
def savings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    if request.method == "POST":
        if 'add_goal' in request.form:
            goal_name = request.form.get("goal_name")
            target_amount = request.form.get("target_amount")
            target_date = request.form.get("target_date")
            
            cursor.execute('''INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
                              VALUES (?, ?, ?, 0, ?)''', (user_id, goal_name, target_amount, target_date))
        elif 'update_amount' in request.form:
            goal_id = request.form.get("goal_id")
            new_amount = request.form.get("current_amount")
            
            cursor.execute("UPDATE savings_goals SET current_amount = ? WHERE id = ? AND user_id = ?", 
                           (new_amount, goal_id, user_id))
            
        conn.commit()
        return redirect(url_for("savings"))
    cursor.execute("SELECT * FROM savings_goals WHERE user_id = ?", (user_id,))
    goals = cursor.fetchall()
    conn.close()
    return render_template("savings.html", goals=goals) 



@app.route("/delete_goal/<int:goal_id>")
def delete_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM savings_goals WHERE id=? AND user_id=?", 
        (goal_id, session["user_id"])
    )
    
    # ၄။ ပြောင်းလဲမှုများကို သိမ်းဆည်းပြီး connection ပိတ်မည်
    conn.commit()
    conn.close()
    flash("Savings goal deleted successfully!", "success")
    return redirect(url_for("savings")) 

# add-income updated
@app.route("/add_income", methods=["GET", "POST"])
def add_income():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Error တက်ရင် User ရိုက်ထားတဲ့ data တွေ ပြန်ပေါ်နေဖို့ form_data ကို သုံးမယ်
    form_data = {}

    if request.method == "POST":
        form_data = request.form
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()
        date_input = request.form.get("date") or date.today().strftime("%Y-%m-%d")

        # 🚩 1. Input Field Required Validation (အကုန်ဖြည့်ရန် စစ်ဆေးခြင်း)
        if not category or not amount_str:
            flash(t("all_fields_required") if LANGUAGES else "Category and Amount are required!", "danger")
            return render_template(
                "income_form.html", 
                mode="add", 
                categories=INCOME_CATEGORIES, 
                form_data=form_data,
                current_date=date_input
            )

        # 🚩 2. Numeric Validation (ဂဏန်းမှန်မမှန် စစ်ဆေးခြင်း)
        try:
            amount = float(amount_str)
            if amount <= 0:
                flash(t("amount_min_error") if LANGUAGES else "Amount must be greater than zero!", "danger")
                return render_template("income_form.html", mode="add", categories=INCOME_CATEGORIES, form_data=form_data)
        except ValueError:
            flash(t("invalid_amount") if LANGUAGES else "Please enter a valid number for amount!", "danger")
            return render_template("income_form.html", mode="add", categories=INCOME_CATEGORIES, form_data=form_data)

        # 🚩 3. Database ထဲသို့ ထည့်သွင်းခြင်း
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO income(user_id, date, category, amount, description) VALUES(?,?,?,?,?)",
                (session["user_id"], date_input, category, amount, description)
            )
            conn.commit()
            conn.close()

            flash(t("income_success") if LANGUAGES else "Income added successfully!", "success")
            return redirect(url_for("dashboard"))
            
        except Exception as e:
            flash(f"Database Error: {str(e)}", "danger")
            return render_template("income_form.html", mode="add", categories=INCOME_CATEGORIES, form_data=form_data)

    # --- GET Request (Page စပွင့်ချိန်) ---
    return render_template(
        "income_form.html",
        mode="add",
        categories=INCOME_CATEGORIES,
        current_date=date.today().strftime("%Y-%m-%d"),
        form_data={}
    )


# add expense updated
from datetime import date
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Initial values
    form_data = {}
    current_date = date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        form_data = request.form
        
      
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()
        date_input = request.form.get("date") or current_date
        confirm = request.form.get("confirm")

       
        if not category or not amount_str or not date_input:
            flash(t("all_fields_required"), "danger")
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 form_data=form_data)

  
        try:
            amount = float(amount_str)
            if amount <= 0:
                flash(t("amount_min_error"), "danger")
                return render_template("expense_form.html", 
                                     categories=EXPENSE_CATEGORIES, 
                                     current_date=date_input, 
                                     mode="add", 
                                     form_data=form_data)
        except ValueError:
            flash(t("invalid_amount"), "danger")
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 form_data=form_data)

     
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Income စုစုပေါင်း
        cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
        total_income = cursor.fetchone()[0] or 0

        # Expense စုစုပေါင်း
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (session["user_id"],))
        total_expense = cursor.fetchone()[0] or 0

        available_balance = total_income - total_expense

      
        if amount > available_balance:
            flash(f"{t('exceed_balance_msg')} ({available_balance})!", "danger")
            conn.close()
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 form_data=form_data)

   
        if amount == available_balance and confirm != "yes":
            flash(t("confirm_all_balance"), "warning")
            conn.close()
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 show_confirm=True, 
                                 form_data=form_data)

    
        try:
            cursor.execute(
                "INSERT INTO expenses(user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], date_input, category, amount, description)
            )
            conn.commit()
            flash(t("expense_success"), "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 form_data=form_data)
        finally:
            conn.close()

    # GET Request
    return render_template("expense_form.html", 
                         categories=EXPENSE_CATEGORIES, 
                         current_date=current_date, 
                         mode="add", 
                         form_data={})

  

# edit-income
@app.route("/edit_income/<int:income_id>", methods=["GET", "POST"])
def edit_income(income_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Column name ဖြင့် data ခေါ်ယူနိုင်ရန်
    cursor = conn.cursor()

    if request.method == "POST":
        form_data = request.form
        date_input = request.form.get("date")
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()

        # ✅ 1. VALIDATION
        if not amount_str:
            flash(t("amount_required") if LANGUAGES else "Amount is required!", "danger")
            return render_template("income_form.html", categories=INCOME_CATEGORIES, form_data=form_data, mode="edit", income_id=income_id)

        try:
            amount = float(amount_str)
        except ValueError:
            flash(t("invalid_amount") if LANGUAGES else "Invalid amount!", "danger")
            return render_template("income_form.html", categories=INCOME_CATEGORIES, form_data=form_data, mode="edit", income_id=income_id)

        if amount <= 0:
            flash(t("amount_min_error") if LANGUAGES else "Amount must be > 0", "danger")
            return render_template("income_form.html", categories=INCOME_CATEGORIES, form_data=form_data, mode="edit", income_id=income_id)

        # ✅ 2. UPDATE DATABASE
        cursor.execute("""
            UPDATE income 
            SET date=?, category=?, amount=?, description=? 
            WHERE id=? AND user_id=?
        """, (date_input, category, amount, description, income_id, session["user_id"]))
        
        conn.commit()
        conn.close()

        flash(t("income_updated") if LANGUAGES else "Income updated successfully!", "success")
        return redirect(url_for("dashboard"))

    # --- GET REQUEST (LOAD DATA) ---
    cursor.execute(
        "SELECT date, category, amount, description FROM income WHERE id=? AND user_id=?",
        (income_id, session["user_id"])
    )
    record = cursor.fetchone()
    conn.close()

    if not record:
        flash("Record not found!", "danger")
        return redirect(url_for("dashboard"))

    # Template error ကင်းစေရန် လက်ရှိ data ကို dictionary အဖြစ်ပြောင်းလဲခြင်း
    current_form_data = {
        'date': record['date'],
        'category': record['category'],
        'amount': record['amount'],
        'description': record['description']
    }

    return render_template(
        "income_form.html",
        categories=INCOME_CATEGORIES,
        form_data=current_form_data,
        mode="edit",
        income_id=income_id
    )
# # ---- Delete Income ----
# @app.route("/delete_income/<int:income_id>")
# def delete_income(income_id):
#     if "user_id" not in session:
#         return redirect(url_for("login"))
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM income WHERE id=? AND user_id=?", (income_id, session["user_id"]))
#     conn.commit()
#     conn.close()
#     flash("Income deleted!", "success")
#     return redirect(url_for("dashboard"))

# delete updated 1
@app.route("/delete_income/<int:income_id>", methods=["GET", "POST"])
def delete_income(income_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- POST: User က 'Confirm Delete' ခလုတ်ကို နှိပ်လိုက်သောအခါ ---
    if request.method == "POST":
        cursor.execute("DELETE FROM income WHERE id=? AND user_id=?", (income_id, session["user_id"]))
        conn.commit()
        conn.close()
        flash(t("delete_success") if LANGUAGES else "Income deleted successfully!", "success")
        return redirect(url_for("dashboard"))

    # --- GET: ဖျက်ရမည့် အချက်အလက်ကို အရင်ပြရန် ---
    cursor.execute("SELECT date, category, amount, description FROM income WHERE id=? AND user_id=?", 
                   (income_id, session["user_id"]))
    record = cursor.fetchone()
    conn.close()

    if not record:
        flash("Record not found!", "danger")
        return redirect(url_for("dashboard"))

    # ဤနေရာတွင် mode="delete" ဟု သတ်မှတ်ပြီး ပို့ပေးပါမည်
    return render_template(
        "income_form.html",
        mode="delete",
        income_id=income_id,
        form_data=record,
        categories=INCOME_CATEGORIES
    )


# edit expense updated
@app.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        form_data = request.form
        date_input = request.form.get("date")
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()
        if not amount_str:
            flash(t("amount_required") if LANGUAGES else "Amount is required!", "danger")
            return render_template("expense_form.html", categories=EXPENSE_CATEGORIES, form_data=form_data, mode="edit", expense_id=expense_id)

        try:
            amount = float(amount_str)
        except ValueError:
            flash(t("invalid_amount") if LANGUAGES else "Invalid amount!", "danger")
            return render_template("expense_form.html", categories=EXPENSE_CATEGORIES, form_data=form_data, mode="edit", expense_id=expense_id)

        if amount <= 0:
            flash(t("amount_min_error") if LANGUAGES else "Amount must be > 0", "danger")
            return render_template("expense_form.html", categories=EXPENSE_CATEGORIES, form_data=form_data, mode="edit", expense_id=expense_id)
        cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
        total_income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND id<>?", (session["user_id"], expense_id))
        total_expense_except_current = cursor.fetchone()[0] or 0

        available_balance = total_income - total_expense_except_current

        if amount > available_balance:
            flash(f"{t('exceed_balance_msg') if LANGUAGES else 'Exceeds balance!'} ({available_balance})", "danger")
            return render_template("expense_form.html", categories=EXPENSE_CATEGORIES, form_data=form_data, mode="edit", expense_id=expense_id)

        # ✅ 3. UPDATE DATABASE
        cursor.execute(
            "UPDATE expenses SET date=?, category=?, amount=?, description=? WHERE id=? AND user_id=?",
            (date_input, category, amount, description, expense_id, session["user_id"])
        )
        conn.commit()
        conn.close()

        flash(t("update_success") if LANGUAGES else "Updated successfully!", "success")
        return redirect(url_for("dashboard"))

    # --- GET REQUEST (LOAD DATA) ---
    cursor.execute(
        "SELECT date, category, amount, description FROM expenses WHERE id=? AND user_id=?",
        (expense_id, session["user_id"])
    )
    record = cursor.fetchone()
    conn.close()

    if not record:
        flash("Record not found!", "danger")
        return redirect(url_for("dashboard"))

    # record ထဲက data တွေကို form_data အဖြစ်ပြောင်းလဲပေးလိုက်ခြင်း (Template error ကင်းစေရန်)
    current_form_data = {
        'date': record['date'],
        'category': record['category'],
        'amount': record['amount'],
        'description': record['description']
    }

    return render_template(
        "expense_form.html",
        categories=EXPENSE_CATEGORIES,
        form_data=current_form_data,
        mode="edit",
        expense_id=expense_id
    )

# ---- Delete Expense ----
# @app.route("/delete_expense/<int:expense_id>")
# def delete_expense(expense_id):
#     if "user_id" not in session:
#         return redirect(url_for("login"))
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, session["user_id"]))
#     conn.commit()
#     conn.close()
#     flash("Expense deleted!", "success")
#     return redirect(url_for("dashboard"))

# delete updated 1
from datetime import datetime

@app.route("/delete_expense/<int:expense_id>", methods=["GET", "POST"])
def delete_expense(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Dictionary ကဲ့သို့ သုံးနိုင်ရန်
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, session["user_id"]))
        conn.commit()
        conn.close()
        flash("Expense deleted successfully!", "success")
        return redirect(url_for("dashboard"))

    # GET: အချက်အလက်များကို ဆွဲထုတ်ခြင်း
    cursor.execute("SELECT date, category, amount, description FROM expenses WHERE id=? AND user_id=?", 
                   (expense_id, session["user_id"]))
    record = cursor.fetchone()
    conn.close()

    if not record:
        flash("Expense not found!", "danger")
        return redirect(url_for("dashboard"))

    # Today's date for fallback
    today = datetime.now().strftime('%Y-%m-%d')

    return render_template(
        "expense_form.html",
        mode="delete",
        expense_id=expense_id,
        form_data=record,      # sqlite3.Row object
        current_date=today,    # Variable name current_date ဟု ပေးထားပါ
        categories=EXPENSE_CATEGORIES
    )
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



# quiz updated 2
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # 1. Initialize session if missing
    if "quiz_questions" not in session or "quiz_index" not in session:
        session["quiz_questions"] = random.sample(QUIZ_QUESTIONS, min(len(QUIZ_QUESTIONS), QUIZ_TOTAL_QUESTIONS))
        session["quiz_index"] = 0
        session["quiz_score"] = 0
        session["quiz_start_time"] = time.time()

    quiz_questions = session.get("quiz_questions", [])
    index = session.get("quiz_index", 0)
    # If the index is out of bounds, finish the quiz immediately
    if index >= len(quiz_questions):
        return redirect(url_for("quiz_result"))

    # 3. Timer Logic
    start_time = session.get("quiz_start_time", time.time())
    elapsed_time = int(time.time() - start_time)
    remaining_time = QUIZ_TIME_LIMIT - elapsed_time

    if remaining_time <= 0:
        return redirect(url_for("quiz_result"))

    # 4. POST: Answer Submission
    if request.method == "POST":
        selected = request.form.get("option")
        
        # Double check index before grading
        if index < len(quiz_questions):
            correct = quiz_questions[index]["answer"]
            if selected == correct:
                session["quiz_score"] += 1
            
            # Increment index
            session["quiz_index"] += 1
            session.modified = True # Ensure session saves

        # Check if that was the last question
        if session["quiz_index"] >= len(quiz_questions):
            return redirect(url_for("quiz_result"))

        return redirect(url_for("quiz"))


    # Since we performed the safety check in step 2, this is now safe
    question = quiz_questions[index]

    return render_template(
        "quiz.html",
        question=question,
        current=index + 1,
        total=len(quiz_questions),
        remaining_time=remaining_time
    )


# quiz updated 2
@app.route("/quiz/result")
def quiz_result():
    if "user_id" not in session:
        return redirect(url_for("login"))

    score = session.get("quiz_score", 0)
    total = len(session.get("quiz_questions", []))

    return render_template("quiz_result.html", score=score, total=total)



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




translator = Translator()


# translated updated
def t(key, is_user_data=False):
    # session ထဲမှာ language မရှိရင် default 'en' ယူမယ်
    lang = session.get('language', 'en') 
    if is_user_data and key:
        if lang == 'mm':
            try:
                return translator.translate(key, dest='my').text
            except:
                return key
        return key

    # Static UI စာသားဖြစ်လျှင် Dictionary ထဲမှာရှာမယ်
    translated = LANGUAGES.get(lang, LANGUAGES['en']).get(key)
    if translated:
        return translated

    # Dictionary မှာမရှိရင် Category ဖြစ်နိုင်လို့ Google Translate သုံးမယ်
    if lang == 'mm' and key:
        try:
            return translator.translate(key, dest='my').text
        except:
            return key
            
    return key


@app.context_processor
def inject_translate():
    return dict(t=t)

# ၃။ Language Switcher
@app.route('/set_lang/<lang>')
def set_lang(lang):
    session['language'] = lang
    return redirect(request.referrer or url_for('dashboard'))


# forgot password 
# Mail Configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='minminphyo770@gmail.com',
    MAIL_PASSWORD='fqodrfmwvygkuxdl',
    MAIL_DEFAULT_SENDER='minminphyo770@gmail.com'
)
mail = Mail(app)

# 3 updated reset password
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if 'reset_email' not in session:
        flash("Please verify your email first.", "warning")
        return redirect(url_for('forgot_password'))

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # 1. Validation စစ်ဆေးခြင်း
        if not new_password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("reset_password.html")

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("reset_password.html")

        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("reset_password.html")

        # 2. Password ကို Hash လုပ်ခြင်း (လုံခြုံရေးအတွက်)
        hashed_password = generate_password_hash(new_password)
        email = session.get('reset_email')

        # 3. Database ထဲတွင် Update လုပ်ခြင်း
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            # User table ထဲက သက်ဆိုင်ရာ email ပိုင်ရှင်ရဲ့ password ကို update လုပ်မယ်
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
            conn.commit()
            
            # Row တစ်ခုခု အမှန်တကယ် ပြောင်းလဲသွားသလား စစ်ဆေးခြင်း
            if cursor.rowcount == 0:
                flash("Error: User not found.", "danger")
                return redirect(url_for('forgot_password'))
                
            conn.close()

            # 4. အောင်မြင်ရင် Session များကို ရှင်းထုတ်ပြီး Login သို့ ပို့ခြင်း
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            
            flash("Success! Your password has been updated. Please login.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Database Error: {e}")
            flash("An error occurred while updating password.", "danger")
            return render_template("reset_password.html")

    return render_template("reset_password.html")


# 1 updated
# @app.route("/forgot_password", methods=["GET", "POST"])
# def forgot_password():
#     if request.method == "POST":
#         email = request.form.get("email").strip()
        
#         # OTP ထုတ်ခြင်းနှင့် Session သိမ်းခြင်း (အရင်အတိုင်း)
#         otp = ''.join(random.choices(string.digits, k=6))
#         session['reset_otp'] = otp
#         session['reset_email'] = email

#         # --- Email Sending Logic Start ---
#         msg = Message(
#             subject="Your Password Reset OTP",
#             sender=app.config['MAIL_USERNAME'],
#             recipients=[email]
#         )
#         msg.body = f"Hello,\n\nYour verification code is: {otp}\n\nThis code will expire in 10 minutes."

#         try:
#             mail.send(msg)
#             print(f"✅ Success: Email sent to {email}")
#             flash("OTP code has been sent to your email!", "success")
#             return redirect(url_for("verify_otp"))

#         except smtplib.SMTPAuthenticationError:
#             print("❌ Error: Gmail Authentication Failed. Check App Password.")
#             flash("Server Configuration Error: Invalid Email or App Password.", "danger")
            
#         except smtplib.SMTPConnectError:
#             print("❌ Error: Could not connect to Gmail SMTP Server.")
#             flash("Network Error: Could not connect to the mail server.", "danger")
            
#         except Exception as e:
#             # တခြား မထင်မှတ်ထားတဲ့ error များအတွက်
#             print(f"❌ Unexpected Error: {str(e)}")
#             flash(f"An unexpected error occurred: {str(e)}", "danger")
        
#         # --- Email Sending Logic End ---

#     return render_template("forgot_password.html")


# @app.route("/verify-otp", methods=["GET", "POST"])
# def verify_otp():
#     if 'reset_otp' not in session:
#         return redirect(url_for('forgot_password'))

#     if request.method == "POST":
#         user_otp = request.form.get("otp")
#         if user_otp == session.get('reset_otp'):
#             flash("OTP Verified!", "success")
#             return redirect(url_for('reset_password')) 
#         else:
#             flash("Invalid OTP code. Please try again.", "danger")
            
#     return render_template("verify_otp.html") 


# otp expire testing
from flask_mail import Message
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email").strip()
        
        # ၁။ Database ထဲတွင် User ရှိမရှိ အမှန်တကယ် စစ်ဆေးခြင်း
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()
        except Exception as e:
            flash("Database Connection Error: " + str(e), "danger")
            return redirect(url_for('forgot_password'))

        if not user:
            # User မရှိပါက Error ပြမည်
            flash("ဤအီးမေးလ်ဖြင့် အကောင့်ဖွင့်ထားခြင်း မရှိပါ။", "danger")
            return redirect(url_for('forgot_password'))

        # ၂။ User ရှိပါက ၆ လုံးပါသော OTP နှင့် Session/Timestamp သိမ်းခြင်း
        otp = ''.join(random.choices(string.digits, k=6))
        session['reset_email'] = email
        session['reset_otp'] = otp
        session['otp_created_at'] = time.time()  # ၁ မိနစ်သက်တမ်းအတွက် လက်ရှိအချိန်မှတ်ခြင်း

        # ၃။ Flask-Mail ဖြင့် Email ပို့သည့် Logic
        msg = Message(
            subject="Password Reset Verification Code",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"မင်္ဂလာပါ၊\n\nစကားဝှက်အသစ်လဲလှယ်ရန် သင်၏ OTP ကုဒ်မှာ: {otp} ဖြစ်ပါသည်။\n\nဤကုဒ်သည် ၁ မိနစ်အတွင်းသာ အကျုံးဝင်ပါသည်။"

        try:
            mail.send(msg)
            print(f"✅ Success: Email sent to {email} | OTP: {otp}")
            flash("OTP ကုဒ်ကို အီးမေးလ်သို့ ပို့လိုက်ပါပြီ။ (သက်တမ်း ၁ မိနစ်)", "success")
            return redirect(url_for('verify_otp'))

        except smtplib.SMTPAuthenticationError:
            print("❌ Error: Gmail Authentication Failed.")
            flash("Server Configuration Error: အီးမေးလ်ပို့ရန် စနစ်ချို့ယွင်းနေပါသည်။", "danger")
            
        except smtplib.SMTPConnectError:
            print("❌ Error: SMTP Server Connection Failed.")
            flash("Network Error: အီးမေးလ်ဆာဗာနှင့် ချိတ်ဆက်၍မရပါ။", "danger")
            
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
            flash(f"မထင်မှတ်ထားသော အမှားတစ်ခု ဖြစ်ပေါ်ခဲ့သည်: {str(e)}", "danger")
        
    return render_template("forgot_password.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    # ၁။ Session ထဲမှာ OTP ရှိမရှိ အရင်စစ်ဆေးမည်
    if 'reset_otp' not in session or 'otp_created_at' not in session:
        flash("ကျေးဇူးပြု၍ OTP အရင်တောင်းခံပါ။", "warning")
        return redirect(url_for('forgot_password'))

    if request.method == "POST":
        user_otp = request.form.get("otp")
        current_time = time.time()
        created_at = session.get('otp_created_at', 0)

        # ၂။ ၁ မိနစ် (၆၀ စက္ကန့်) သက်တမ်းကုန်မကုန် စစ်ဆေးခြင်း
        # (current_time - created_at) သည် OTP ထုတ်ပေးခဲ့စဉ်ကအချိန်နှင့် ယခုအချိန် ကွာခြားချက်ဖြစ်သည်
        if current_time - created_at > 60:
            # သက်တမ်းကုန်သွားပါက Session ဒေတာများကို ဖျက်ပစ်မည်
            session.pop('reset_otp', None)
            session.pop('otp_created_at', None)
            flash("OTP သက်တမ်းကုန်ဆုံးသွားပါပြီ။ အသစ်ပြန်တောင်းပါ။", "danger")
            return redirect(url_for('forgot_password'))

        # ၃။ OTP ကုဒ် မှန်မမှန် စစ်ဆေးခြင်း
        if user_otp == session.get('reset_otp'):
            # လုံခြုံရေးအတွက် OTP ကို session ထဲမှ ဖျက်ထုတ်မည် (တစ်ခါသုံးဖြစ်စေရန်)
            session.pop('reset_otp', None)
            session.pop('otp_created_at', None)
            
            # Password Reset လုပ်ခွင့်ပြုရန် Flag တစ်ခုသတ်မှတ်ခြင်း
            session['otp_verified'] = True 
            
            flash("OTP အောင်မြင်ပါသည်။ စကားဝှက်အသစ် ပြောင်းလဲနိုင်ပါပြီ။", "success")
            return redirect(url_for('reset_password'))
        else:
            # ကုဒ်မှားယွင်းပါက Error ပြမည်
            flash("ကုဒ်နံပါတ် မှားယွင်းနေပါသည်။ ပြန်လည်စစ်ဆေးပါ။", "danger")

    return render_template("verify_otp.html")

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True)
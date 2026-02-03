from flask import Flask, render_template, request, redirect, url_for, session, flash
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

        # ===== General =====
        "welcome": "Welcome back",
        "login_success": "Login successful!",
        "logout_success": "Logged out!",
        "register_success": "Registration successful! Please login.",
        
        # register requirement
        "register_title": "Create Account",
        "register_subtitle": "Start tracking your income & expenses 💰",
        "username": "Username",
        "username_placeholder": "Enter your username",
        "email": "Email",
        "email_placeholder": "example@email.com",
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
        "reset": "Reset",
        "quick_filter": "Quick Filter",
        "all": "All",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "yearly": "Yearly",
        "total_income": "Total Income",
        "total_expense": "Total Expense",
        "balance": "Balance",
        "add_income": "+ Add Income",
        "add_expense": "+ Add Expense",
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
        
        # pagination
        "prev":"Prev",
        "next":"Next",
        
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
        "records": "Records",
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
        "cancel":"Home",
        
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
        "reset": "Restart Quiz"
        

    },

    "mm": {
        # ===== App =====
        "app_title": "ငွေထွက်ထိန်းခြင်း",
        "dashboard": "ဝင်ငွေနှင့် ကုန်ကျစရိတ် ဒက်ရှ်ဘုတ်",
        "welcome":"အားလုံးကို ကြိုဆိုပါတယ် ချစ်တို့ရေ",

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
        "reset": "ပြန်သတ်မှတ်မည်",
        "quick_filter": "အမြန်စစ်ထုတ်ရန်",
        "all": "အားလုံး",
        "weekly": "အပတ်စဉ်",
        "monthly": "လစဉ်",
        "yearly": "နှစ်စဉ်",
        "total_income": "စုစုပေါင်း ဝင်ငွေ",
        "total_expense": "စုစုပေါင်း အသုံးစရိတ်",
        "balance": "လက်ကျန်ငွေ",
        "add_income": "+ ဝင်ငွေ ထည့်မည်",
        "add_expense": "+ အသုံးစရိတ် ထည့်မည်",
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
        
        # pagination
        "prev":"ယခင်",
        "next":"နောက်တစ်ခု",
        
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
        "records": "မှတ်တမ်းများ",
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
        "cancel":"ပင်မစာမျက်နှာ",
        
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
        "reset": "အစကပြန်စမည်"
    }
}


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

#         # if len(password) < 6:
#         #     flash("Password must be at least 6 characters long!", "danger")
#         #     return render_template("register.html")
        
#         if not re.match(r"^(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{6,}$", password):
#               flash("Password must be at least 6 characters long and include a number and a special character!",
#                      "danger")
#               return render_template("register.html")


#         # ---- Save to database with password hash ----
#         try:
#             hashed_password = generate_password_hash(password)  # 🔑 hash password
#             conn = sqlite3.connect(DB_NAME)
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
#                 (username, email, hashed_password)
#             )
            
#             conn.commit()
#             conn.close()

#             flash("Registration successful! Please login.", "success")
#             return redirect(url_for("login"))

#         except sqlite3.IntegrityError:
#             flash("Username or email already exists!", "danger")
#             return render_template("register.html")

#     return render_template("register.html")


# test register updated
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
@app.route("/register", methods=["GET", "POST"])
def register():
    form_data = {}
    if request.method == "POST":
        # ၁။ Form data များကို ဖမ်းယူခြင်း
        form_data = request.form
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        avatar_file = request.files.get("avatar")

        # ၂။ အခြေခံ Validation များစစ်ဆေးခြင်း
        if not username or not email or not password:
            flash(t("all_fields_required"), "danger")
            return render_template("register.html", form_data=form_data)

        if not EMAIL_REGEX.match(email):
            flash(t("invalid_email"), "danger")
            return render_template("register.html", form_data=form_data)

        # Password Policy (အနည်းဆုံး ၆ လုံး၊ နံပါတ် နှင့် သင်္ကေတ ပါရမည်)
        if not re.match(r"^(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{6,}$", password):
            flash(t("password_policy_error"), "danger")
            return render_template("register.html", form_data=form_data)

        # ၃။ Avatar ဖိုင်ကို စစ်ဆေးခြင်းနှင့် သိမ်းဆည်းခြင်း
        avatar_filename = "default_avatar.png"  # ပုံမတင်လျှင် သုံးမည့် default အမည်

        if avatar_file and avatar_file.filename != '':
            if allowed_file(avatar_file.filename):
                # ဖိုင်အမည်ကို လုံခြုံအောင်ပြုလုပ်ပြီး username တွဲပေးခြင်း (အမည်တူမထပ်စေရန်)
                ext = avatar_file.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"{username}_{avatar_file.filename}")
                avatar_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                avatar_filename = filename
            else:
                flash(t("invalid_file_format"), "danger")
                return render_template("register.html", form_data=form_data)

        # ၄။ Database ထဲသို့ ထည့်သွင်းခြင်း
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
    # Clear the session
    session.clear()

    # Get current language (default to 'en')
    lang = session.get("lang", "en")

    # Flash message using language dictionary
    flash(LANGUAGES.get(lang, LANGUAGES["en"]).get("logout_success", "Logged out!"), "success")

    # Redirect to login page
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

#     return render_template(
#         "income_form.html",
#         mode="add",
#         categories=INCOME_CATEGORIES,
#         current_date=date.today().strftime("%Y-%m-%d")
#     )


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

# add expense 
# @app.route("/add_expense", methods=["GET", "POST"])
# def add_expense():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     if request.method == "POST":
#         category = request.form["category"]
#         amount = float(request.form["amount"])
#         description = request.form["description"]
#         date_input = request.form.get("date")
#         confirm = request.form.get("confirm")  # <-- confirm flag

#         # Calculate balance
#         cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
#         total_income = cursor.fetchone()[0] or 0

#         cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (session["user_id"],))
#         total_expense = cursor.fetchone()[0] or 0

#         available_balance = total_income - total_expense

#         # ❌ BLOCK
#         if amount > available_balance:
#             flash(f"Expense exceeds available balance ({available_balance})!", "danger")
#             conn.close()
#             return redirect(url_for("add_expense"))

#         # ⚠ CONFIRM REQUIRED
#         if amount == available_balance and confirm != "yes":
#             flash(
#                 "This expense will use ALL your remaining balance. Please confirm.",
#                 "warning"
#             )
#             conn.close()
#             return render_template(
#                 "expense_form.html",
#                 categories=EXPENSE_CATEGORIES,
#                 current_date=date_input,
#                 mode="add",
#                 show_confirm=True,
#                 form_data=request.form
#             )

#         # ✅ INSERT
#         cursor.execute(
#             "INSERT INTO expenses(user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
#             (session["user_id"], date_input, category, amount, description)
#         )
#         conn.commit()
#         conn.close()

#         flash("Expense added successfully!", "success")
#         return redirect(url_for("dashboard"))

#     conn.close()
#     return render_template(
#         "expense_form.html",
#         categories=EXPENSE_CATEGORIES,
#         current_date=date.today().strftime("%Y-%m-%d"),
#         mode="add",
#         show_confirm=False
#     )


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
        
        # Form Data ဆွဲထုတ်ခြင်း
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()
        date_input = request.form.get("date") or current_date
        confirm = request.form.get("confirm")

        # 🚩 1. Required Fields Validation (မဖြစ်မနေ ဖြည့်ရမည့်နေရာများ စစ်ဆေးခြင်း)
        if not category or not amount_str or not date_input:
            flash(t("all_fields_required"), "danger")
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 form_data=form_data)

        # 🚩 2. Amount Validation (ဂဏန်း မှန်မမှန်နှင့် သုညထက်ကြီးမကြီး စစ်ဆေးခြင်း)
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

        # 🚩 3. Balance Calculation & Check
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Income စုစုပေါင်း
        cursor.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (session["user_id"],))
        total_income = cursor.fetchone()[0] or 0

        # Expense စုစုပေါင်း
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (session["user_id"],))
        total_expense = cursor.fetchone()[0] or 0

        available_balance = total_income - total_expense

        # ❌ Case: လက်ကျန်ငွေထက် ပိုသုံးခြင်း
        if amount > available_balance:
            flash(f"{t('exceed_balance_msg')} ({available_balance})!", "danger")
            conn.close()
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 form_data=form_data)

        # ⚠ Case: Balance အကုန်သုံးမည်ဆိုပါက Confirm တောင်းခြင်း
        if amount == available_balance and confirm != "yes":
            flash(t("confirm_all_balance"), "warning")
            conn.close()
            return render_template("expense_form.html", 
                                 categories=EXPENSE_CATEGORIES, 
                                 current_date=date_input, 
                                 mode="add", 
                                 show_confirm=True, 
                                 form_data=form_data)

        # ✅ 4. Data Insertion (ဒေတာ သိမ်းဆည်းခြင်း)
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
         record=record,
         mode="edit",
        categories=INCOME_CATEGORIES,

    )

# edit-income updated 
# @app.route("/edit_income/<int:income_id>", methods=["GET", "POST"])
# def edit_income(income_id):
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = sqlite3.connect(DB_NAME)
#     conn.row_factory = sqlite3.Row  # Dictionary ပုံစံမျိုး ခေါ်သုံးလို့ရအောင်
#     cursor = conn.cursor()

#     if request.method == "POST":
#         # Form ကလာတဲ့ data အသစ်များကို ဖမ်းယူခြင်း
#         form_data = request.form
#         date_input = request.form.get("date")
#         category = request.form.get("category", "").strip()
#         amount_str = request.form.get("amount", "").strip()
#         description = request.form.get("description", "").strip()

#         # Validation (Amount ပါမပါ စစ်ဆေးခြင်း)
#         if not amount_str or not category:
#             flash(t("all_fields_required"), "danger")
#             return render_template("income_form.html", mode="edit", categories=INCOME_CATEGORIES, form_data=form_data)

#         try:
#             amount = float(amount_str)
#             cursor.execute(
#                 "UPDATE income SET date=?, category=?, amount=?, description=? WHERE id=? AND user_id=?",
#                 (date_input, category, amount, description, income_id, session["user_id"])
#             )
#             conn.commit()
#             conn.close()
#             flash(t("update_success"), "success")
#             return redirect(url_for("dashboard"))
#         except ValueError:
#             flash(t("invalid_amount"), "danger")
#             return render_template("income_form.html", mode="edit", categories=INCOME_CATEGORIES, form_data=form_data)

#     # --- GET REQUEST (Edit လုပ်ရန် Page စပွင့်ချိန်) ---
#     cursor.execute(
#         "SELECT date, category, amount, description FROM income WHERE id=? AND user_id=?",
#         (income_id, session["user_id"])
#     )
#     record = cursor.fetchone()
#     conn.close()

#     if not record:
#         flash("Record not found!", "danger")
#         return redirect(url_for("dashboard"))

#     # Database ကလာတဲ့ data တွေကို HTML ကနားလည်တဲ့ form_data ပုံစံသို့ ပြောင်းလဲခြင်း
#     current_values = {
#         "date": record["date"],
#         "category": record["category"],
#         "amount": record["amount"],
#         "description": record["description"]
#     }

#     return render_template(
#         "income_form.html",
#         mode="edit",
#         categories=INCOME_CATEGORIES,
#         form_data=current_values, # အခု နာမည်ကို form_data လို့ ပေးလိုက်တဲ့အတွက် HTML နဲ့ ကွက်တိဖြစ်သွားပါပြီ
#         income_id=income_id
#     )
# # ---- Delete Income ----
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
# @app.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
# def edit_expense(expense_id):
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = sqlite3.connect(DB_NAME)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()

#     if request.method == "POST":
#         date_input = request.form.get("date")
#         category = request.form.get("category", "").strip()
#         amount_str = request.form.get("amount", "").strip()
#         description = request.form.get("description", "").strip()
       

#         # ✅ VALIDATION
#         if not amount_str:
#             flash("Amount is required!", "danger")
#             conn.close()
#             return redirect(url_for("edit_expense", expense_id=expense_id))

#         try:
#             amount = float(amount_str)
#         except ValueError:
#             flash("Invalid amount value!", "danger")
#             conn.close()
#             return redirect(url_for("edit_expense", expense_id=expense_id))

#         if amount <= 0:
#             flash("Amount must be greater than zero!", "danger")
#             conn.close()
#             return redirect(url_for("edit_expense", expense_id=expense_id))

#         # ---- BALANCE CHECK (exclude current expense) ----
#         cursor.execute(
#             "SELECT SUM(amount) FROM income WHERE user_id=?",
#             (session["user_id"],)
#         )
#         total_income = cursor.fetchone()[0] or 0

#         cursor.execute(
#             "SELECT SUM(amount) FROM expenses WHERE user_id=? AND id<>?",
#             (session["user_id"], expense_id)
#         )
#         total_expense_except_current = cursor.fetchone()[0] or 0

#         available_balance = total_income - total_expense_except_current

#         if amount > available_balance:
#             flash(
#                 f"Expense exceeds available balance ({available_balance})!",
#                 "danger"
#             )
#             conn.close()
#             return redirect(url_for("edit_expense", expense_id=expense_id))

#         # ---- UPDATE EXPENSE ----
#         cursor.execute(
#             """
#             UPDATE expenses
#             SET date=?, category=?, amount=?, description=?
#             WHERE id=? AND user_id=?
#             """,
#             (date_input,category, amount, description, expense_id, session["user_id"])
#         )

#         conn.commit()
#         conn.close()

#         flash("Expense updated successfully!", "success")
#         return redirect(url_for("dashboard"))

#     # ---- GET REQUEST (LOAD RECORD) ----
#     cursor.execute(
#         """
#         SELECT date,category, amount, description
#         FROM expenses
#         WHERE id=? AND user_id=?
#         """,
#         (expense_id, session["user_id"])
#     )
#     record = cursor.fetchone()
#     conn.close()

#     if not record:
#         flash("Record not found!", "danger")
#         return redirect(url_for("dashboard"))

#     return render_template(
#         "expense_form.html",
#         categories=EXPENSE_CATEGORIES,
#         record=record,
#         mode="edit"
#     )

# edit expense updated
@app.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        # Form ကလာတဲ့ data တွေကို စုစည်းမယ် (Error တက်ရင် template ပြန်ပို့ဖို့)
        form_data = request.form
        date_input = request.form.get("date")
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "").strip()
        description = request.form.get("description", "").strip()

        # ✅ 1. VALIDATION (Amount ရှိမရှိ စစ်ဆေးခြင်း)
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

        # ✅ 2. BALANCE CHECK (ယခုပြင်မည့် record ကို ချန်လှပ်၍ တွက်ချက်ခြင်း)
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



# eng myanmar version
# def t(key):
#     lang = session.get("lang", "en")
#     return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)

# @app.context_processor
# def inject_lang():
#     return dict(t=t)


# @app.route("/set_language/<lang>")
# def set_language(lang):
#     # only accept 'en' or 'mm'
#     if lang not in ["en", "mm"]:
#         lang = "en"
#     session["lang"] = lang

#     # redirect back to the page user was on
#     return redirect(request.referrer or url_for("dashboard"))


# --- ၂။ Hybrid Translation Logic ---
translator = Translator()

# --- t() function logic ---
# @app.context_processor
# def inject_translate():
#     def t(key, is_user_data=False):
#         lang = session.get('language', 'en') # en သို့မဟုတ် mm
#         # ၁။ User ရိုက်ထားတဲ့ စာသား (Description) ဖြစ်လျှင် Google Translate သုံးမည်
#         if is_user_data and key:
#             if lang == 'mm':
#                 try:
#                     return translator.translate(key, dest='my').text
#                 except:
#                     return key # Error ဖြစ်လျှင် မူလစာသားအတိုင်းပြမည်
#             return key

#         # ၂။ Static UI စာသားဖြစ်လျှင် Dictionary ထဲမှာရှာမည်
#         # Dictionary မှာမရှိရင် Category ဖြစ်နိုင်လို့ google translate ဆီ တစ်ခါထပ်ပို့ကြည့်မယ်
#         translated = LANGUAGES.get(lang, LANGUAGES['en']).get(key)
#         if translated:
#             return translated
#         # ၃။ Dictionary မှာမရှိတဲ့ Category မျိုးဆိုလျှင် အလိုအလျောက် ဘာသာပြန်ခိုင်းမည်
#         if lang == 'mm' and key:
#             try:
#                 return translator.translate(key, dest='my').text
#             except:
#                 return key
                
#         return key
#     return dict(t=t)

# # --- Language Switcher Route ---
# @app.route('/set_lang/<lang>')
# def set_lang(lang):
#     session['language'] = lang
#     return redirect(request.referrer or url_for('dashboard'))

# translated updated
# ၁။ t function ကို Global အနေနဲ့ အပြင်မှာ အရင်ရေးပါ
def t(key, is_user_data=False):
    # session ထဲမှာ language မရှိရင် default 'en' ယူမယ်
    lang = session.get('language', 'en') 
    
    # User ရိုက်ထားတဲ့ စာသား (Description) ဖြစ်လျှင်
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

# ၂။ ပြီးမှ HTML template တွေအတွက် inject လုပ်ပေးပါ
@app.context_processor
def inject_translate():
    return dict(t=t) # အပေါ်က function ကိုပဲ ပြန်ညွှန်းလိုက်တာပါ

# ၃။ Language Switcher
@app.route('/set_lang/<lang>')
def set_lang(lang):
    session['language'] = lang
    return redirect(request.referrer or url_for('dashboard'))

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True)
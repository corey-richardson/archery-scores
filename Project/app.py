import sqlite3
from datetime import date

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from archeryutils import load_rounds

from helpers import login_required

# Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to SQLite database
db_path = "./static/database.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
db = conn.cursor()

# if __name__ == "__main__":
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     password =  generate_password_hash("password")
#     cursor.execute("""
#         INSERT INTO Archer (first_name,
#                             last_name,
#                             username,
#                             password,
#                             birth_date,
#                             default_category,
#                             default_bowstyle) 
#         VALUES (
#             'TEST', 'USER', 'TEST-USER', ?, '2024-08-06', 1, 2
#         );
#     """, (password,))
    
#     conn.commit()
#     print("Test user created successfully.")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/failure")
def failure():
    error_message = request.args.get("ERR_MSG", "Undefined Error.")
    return render_template("failure.html", ERR_MSG=error_message)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
             return redirect(url_for("failure", ERR_MSG="Username field was left empty."))
        if not request.form.get("password"):
            return redirect(url_for("failure", ERR_MSG="Password field was left empty."))

        users = db.execute(
            "SELECT * FROM Archer WHERE username = ?",
            (request.form.get("username"),)
        ).fetchall()
        
        print(users)

        if len(users) != 1 or not check_password_hash(users[0][4], request.form.get("password")):
            return redirect(url_for("failure", ERR_MSG="Username or password invalid!"))

        session["user_id"] = users[0][0]
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")


@app.route("/submit", methods=["get","post"])
@login_required
def submit():
    user_defaults = list(db.execute(
        "SELECT default_bowstyle, default_category FROM Archer WHERE archer_id = ?", 
        str(session["user_id"])
    ))[0]
    print(user_defaults)
    today = date.today().strftime('%Y-%m-%d')
    
    agb_outdoor_imperial = load_rounds.AGB_outdoor_metric
    agb_outdoor_metric = load_rounds.AGB_outdoor_metric
    agb_indoors = load_rounds.AGB_indoor
    wa_indoors = load_rounds.WA_indoor
    unofficial = load_rounds.misc
    
    bowstyles = list(db.execute(
        "SELECT * FROM Bowstyles"
    ))
    
    categories = list(db.execute(
        "SELECT * FROM Categories"
    ))
    
    event_types = list(db.execute(
        "SELECT * FROM EventType"
    ))
    
    rounds = {**agb_indoors, **wa_indoors, **agb_outdoor_imperial, **agb_outdoor_metric, **unofficial}
    
    return render_template("submit.html", 
                           rounds=rounds, 
                           today=today,
                           bowstyles=bowstyles, categories=categories, event_types=event_types,
                           default_bowstyle=user_defaults[0], default_category=user_defaults[1])
    
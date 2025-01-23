import sqlite3
from datetime import date

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from archeryutils import load_rounds
from archeryutils import handicaps as hc
from archeryutils import classifications as class_func

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

if __name__ == "__main__":
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    password =  generate_password_hash("password")
    cursor.execute("""
        INSERT INTO Archer (first_name,
                            last_name,
                            username,
                            password,
                            birth_date,
                            default_category,
                            default_bowstyle) 
        VALUES (
            'TEST', 'USER', 'TEST-USER', ?, '2004-08-06', 1, 2
        );
    """, (password,))
    
    cursor.execute("""
        INSERT INTO ArcherRoles (archer_id, role_id)
        VALUES
            (1, 1),
            (1, 2),
            (1, 3);               
    """)
    
    conn.commit()
    print("Test user created successfully.")

@app.route("/")
@login_required
def index():
    user = db.execute(
        "SELECT first_name, last_name, username, birth_date, default_category, default_bowstyle FROM Archer WHERE archer_id = ?", 
        str(session["user_id"])
    ).fetchone()
    
    birth_year = int(user[3].split('-')[0])
    current_year = date.today().year
    age = current_year - birth_year
    if age >= 21:
        match (user[4]):
            case "Male U21":
                db.execute("UPDATE Archer SET default_category = 'Male' WHERE archer_id = ?", str(session["user_id"]))                
            case "Female U21":
                db.execute("UPDATE Archer SET default_category = 'Female' WHERE archer_id = ?", str(session["user_id"]))                

    return render_template("index.html",
                           user=user, age=age)

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
    agb_outdoor_imperial = load_rounds.AGB_outdoor_metric
    agb_outdoor_metric = load_rounds.AGB_outdoor_metric
    agb_indoors = load_rounds.AGB_indoor
    wa_indoors = load_rounds.WA_indoor
    unofficial = load_rounds.misc
    
    all_round_objects = {**agb_indoors, **wa_indoors, **agb_outdoor_imperial, **agb_outdoor_metric, **unofficial}
    
    if request.method == "POST":
        bowstyle = request.form.get("bowstyle")
        category = request.form.get("category")
        round_name = request.form.get("round")
        date_shot = request.form.get("date_shot")
        event_type = request.form.get("event_type")
        event_name = request.form.get("event_name")
        score = request.form.get("score")
        hits = request.form.get("hits")
        xs = request.form.get("xs") or 0
        tens = request.form.get("tens") or 0
        golds = request.form.get("golds") or 0
        notes = request.form.get("notes")
                        
        category = db.execute("SELECT category_name FROM Categories WHERE category_id = ?", category).fetchone()[0]
        bowstyle = db.execute("SELECT bowstyle_name FROM Bowstyles WHERE bowstyle_id = ?", bowstyle).fetchone()[0]

        sex = "male" if "Male" in category else "female"
        age = "under 21" if "U21" in category else "adult"

        round_handicap = int(hc.handicap_from_score(
            int(score),
            all_round_objects[round_name],
            "AGB",
            int_prec=True
        ))
            
        round_classification = class_func.calculate_agb_indoor_classification(
            int(score),
            round_name,
            bowstyle.lower(),
            sex,
            age
        )

        dozens = sum(pass_i.n_arrows for pass_i in vars(all_round_objects[round_name])['passes']) / 12
        
        cumulative_dozens = db.execute("""
            SELECT 
                SUM(dozens)
            FROM
                Record
            INNER JOIN
                RecordDetails ON Record.record_id = RecordDetails.record_id  
            WHERE
                Record.archer_id = ? AND
                Record.round_classification = ?;                          
        """, (str(session["user_id"]), round_classification,)).fetchone()[0] or 0
        
        db.execute("""
            INSERT INTO Record (archer_id, round_name, date_shot, event_name, event_type, round_handicap, round_classification, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(session["user_id"]), all_round_objects[round_name].name, date_shot, event_name, event_type, round_handicap, round_classification, notes,))

        record_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        db.execute("""
            INSERT INTO RecordDetails (record_id, dozens, cumulative_dozens, score, xs, tens, golds, hits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (record_id, dozens, cumulative_dozens+dozens, int(score), int(xs), int(tens), int(golds), int(hits),))

        db.connection.commit()
    
    today = date.today().strftime('%Y-%m-%d')
    
    user_defaults = db.execute(
        "SELECT default_bowstyle, default_category FROM Archer WHERE archer_id = ?", 
        str(session["user_id"])
    ).fetchone()
    
    bowstyles = db.execute(
        "SELECT * FROM Bowstyles"
    ).fetchall()
    
    categories = db.execute(
        "SELECT * FROM Categories"
    ).fetchall()
    
    event_types = db.execute(
        "SELECT * FROM EventType"
    ).fetchall()
    
    
    
    return render_template("submit.html", 
                           rounds=all_round_objects, 
                           today=today,
                           bowstyles=bowstyles, categories=categories, event_types=event_types,
                           default_bowstyle=user_defaults[0], default_category=user_defaults[1])
    
import sqlite3
from datetime import date

from flask import Flask, render_template
from flask_session import Session
from archeryutils import load_rounds


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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["get","post"])
def submit():
    today = date.today().strftime('%Y-%m-%d')
    
    agb_outdoor_imperial = load_rounds.AGB_outdoor_metric
    agb_outdoor_metric = load_rounds.AGB_outdoor_metric
    agb_indoors = load_rounds.AGB_indoor
    wa_indoors = load_rounds.WA_indoor
    unofficial = load_rounds.misc
    
    bowstyles = list(db.execute(
        "SELECT * FROM Bowstyles"
    ))
    
    event_types = list(db.execute(
        "SELECT * FROM EventType"
    ))
    
    rounds = {**agb_indoors, **wa_indoors, **agb_outdoor_imperial, **agb_outdoor_metric, **unofficial}
    
    return render_template("submit.html", 
                           rounds=rounds, 
                           today=today,
                           bowstyles=bowstyles, event_types=event_types)
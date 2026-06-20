from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "quiz_master_secret_2024"
DB = "quiz.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                answer TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                played_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)
        # Seed questions if empty
        count = db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if count == 0:
            db.executemany("INSERT INTO questions(category,question,option_a,option_b,option_c,option_d,answer) VALUES(?,?,?,?,?,?,?)", [
                ("Python","What is the output of print(type([]))?","<class 'list'>","<class 'tuple'>","<class 'dict'>","<class 'set'>","A"),
                ("Python","Which keyword is used to define a function in Python?","func","define","def","function","C"),
                ("Python","What does len('hello') return?","4","5","6","Error","B"),
                ("Python","Which data type is immutable in Python?","list","dict","set","tuple","D"),
                ("Python","What is the output of 2**3 in Python?","6","8","9","None","B"),
                ("Web","What does HTML stand for?","Hyper Text Markup Language","High Text Machine Language","Hyper Transfer Mode Language","None","A"),
                ("Web","Which CSS property controls text size?","font-weight","font-size","text-size","size","B"),
                ("Web","Which HTML tag is used for a hyperlink?","<link>","<a>","<href>","<url>","B"),
                ("Web","What does CSS stand for?","Cascading Style Sheets","Creative Style System","Computer Style Sheets","Colorful Style Sheets","A"),
                ("Web","Which JavaScript method selects an element by ID?","getElement()","querySelector()","getElementById()","findById()","C"),
                ("SQL","Which SQL command retrieves data?","INSERT","UPDATE","SELECT","DELETE","C"),
                ("SQL","What does PRIMARY KEY ensure?","Uniqueness","Speed","Encryption","Backup","A"),
                ("SQL","Which SQL clause filters results?","ORDER BY","GROUP BY","WHERE","HAVING","C"),
                ("SQL","What does JOIN do in SQL?","Deletes rows","Combines tables","Sorts data","Creates indexes","B"),
                ("SQL","Which command removes all rows from a table?","DROP","DELETE","TRUNCATE","REMOVE","C"),
                ("General","Who invented Python?","Guido van Rossum","Dennis Ritchie","Linus Torvalds","James Gosling","A"),
                ("General","What is the full form of CPU?","Central Processing Unit","Computer Personal Unit","Central Power Unit","Core Processing Unit","A"),
                ("General","Which company developed JavaScript?","Microsoft","Google","Netscape","Apple","C"),
                ("General","What does RAM stand for?","Random Access Memory","Read Access Memory","Run Application Mode","Random Application Memory","A"),
                ("General","What does HTTP stand for?","HyperText Transfer Protocol","High Transfer Text Protocol","Hyper Transfer Text Process","None","A"),
            ])

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

@app.route("/")
def index():
    if "user_id" not in session: return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u, p = request.form["username"], request.form["password"]
        try:
            with get_db() as db:
                db.execute("INSERT INTO users(username,password) VALUES(?,?)", (u, hash_pw(p)))
            return redirect(url_for("login"))
        except: return render_template("register.html", error="Username already exists.")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u, p = request.form["username"], request.form["password"]
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pw(p))).fetchone()
        if user:
            session["user_id"] = user["id"]; session["username"] = user["username"]
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/api/questions/<category>")
def get_questions(category):
    with get_db() as db:
        rows = db.execute("SELECT * FROM questions WHERE category=? ORDER BY RANDOM() LIMIT 5", (category,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/score", methods=["POST"])
def save_score():
    if "user_id" not in session: return jsonify({"error":"Unauthorized"}), 401
    data = request.json
    with get_db() as db:
        db.execute("INSERT INTO scores(user_id,category,score,total,played_at) VALUES(?,?,?,?,?)",
            (session["user_id"], data["category"], data["score"], data["total"], datetime.now().isoformat()))
    return jsonify({"success": True})

@app.route("/api/leaderboard")
def leaderboard():
    with get_db() as db:
        rows = db.execute("""
            SELECT u.username, s.category, MAX(s.score) as best, s.total
            FROM scores s JOIN users u ON s.user_id=u.id
            GROUP BY s.user_id, s.category ORDER BY best DESC LIMIT 20
        """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/my_scores")
def my_scores():
    if "user_id" not in session: return jsonify([])
    with get_db() as db:
        rows = db.execute("SELECT * FROM scores WHERE user_id=? ORDER BY played_at DESC LIMIT 10", (session["user_id"],)).fetchall()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
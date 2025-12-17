from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB = "robot_hub.db"

def get_db():
    return sqlite3.connect(DB)

def init_db():
    """Create the database and tables if they don't exist"""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS robots (
            robot_id TEXT PRIMARY KEY,
            robot_name TEXT NOT NULL,
            ping_count INTEGER DEFAULT 0
        )
    """)
    db.commit()
    db.close()

# Initialize database on startup
if not os.path.exists(DB):
    init_db()

@app.route("/")
def index():
    db = get_db()
    robots = db.execute(
        "SELECT robot_id, robot_name, ping_count FROM robots ORDER BY ping_count DESC"
    ).fetchall()
    db.close()
    return render_template("index.html", robots=robots)

@app.route("/ping", methods=["POST"])
def ping():
    robot_id = request.form. get("robot_id", "R1")
    robot_name = request.form.get("robot_name", "Unknown Robot")

    db = get_db()

    db.execute(
        "INSERT OR IGNORE INTO robots (robot_id, robot_name, ping_count) VALUES (?, ?, 0)",
        (robot_id, robot_name)
    )

    db.execute(
        "UPDATE robots SET ping_count = ping_count + 1 WHERE robot_id = ?",
        (robot_id,)
    )

    db.commit()
    db.close()
    return "PING STORED"

if __name__ == "__main__": 
    app.run(debug=True)
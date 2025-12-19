from flask import Flask, request, render_template, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB = "robot_hub.db"

def get_db():
    return sqlite3.connect(DB)

def init_db():
    """Create the database and tables if they don't exist"""
    db = get_db()

    # Tabel met robot-overzicht (die had je al)
    db.execute("""
        CREATE TABLE IF NOT EXISTS robots (
            robot_id TEXT PRIMARY KEY,
            robot_name TEXT NOT NULL,
            ping_count INTEGER DEFAULT 0,
            last_seen TIMESTAMP,
            last_data TEXT
        )
    """)

    # 🔴 NIEUW: tabel voor ALLE robot logs
    db.execute("""
        CREATE TABLE IF NOT EXISTS robot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id TEXT,
            timestamp TIMESTAMP,
            message TEXT
        )
    """)

    db.commit()
    db.close()


# Initialize database on startup
# Initialize database on startup in the container
init_db()


@app.route("/")
def index():
    db = get_db()
    robots = db.execute(
        "SELECT robot_id, robot_name, ping_count, last_seen, last_data FROM robots ORDER BY ping_count DESC"
    ).fetchall()
    db.close()
    return render_template("index.html", robots=robots)

@app.route("/ping", methods=["POST"])
def ping():
    robot_id = request.form.get("robot_id", "R1")
    robot_name = request. form.get("robot_name", "Unknown Robot")
    robot_data = request.form.get("data", "")

    db = get_db()

    db.execute(
        "INSERT OR IGNORE INTO robots (robot_id, robot_name, ping_count, last_seen, last_data) VALUES (?, ?, 0, ?, ?)",
        (robot_id, robot_name, datetime. now(), robot_data)
    )

    db.execute(
        "UPDATE robots SET ping_count = ping_count + 1, last_seen = ?, last_data = ? WHERE robot_id = ?",
        (datetime.now(), robot_data, robot_id)
    )

    db.commit()
    db.close()
    return "PING STORED"

@app.route("/api/robots")
def api_robots():
    """API endpoint for live data"""
    db = get_db()
    robots = db.execute(
        "SELECT robot_id, robot_name, ping_count, last_seen, last_data FROM robots ORDER BY last_seen DESC"
    ).fetchall()
    db.close()
    
    return jsonify([{
        "robot_id":  r[0],
        "robot_name": r[1],
        "ping_count": r[2],
        "last_seen": r[3],
        "last_data": r[4]
    } for r in robots])

if __name__ == "__main__":  
    app.run(debug=True, host="0.0.0.0")
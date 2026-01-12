from flask import Flask, request, render_template, jsonify
import os
import requests

app = Flask(__name__)

# Set this in Render Environment Variables:
# LAPTOP_API = "https://importance-ambien-relaxation-beer.trycloudflare.com"
LAPTOP_API = os.environ.get("LAPTOP_API")

# Mapping from internal IDs to UI names
ID_MAP = {
    "R1": "Pink Panther",
    "R2": "James Bond",
    "R3": "BDP"
}
NAME_TO_ID = {v: k for k, v in ID_MAP.items()}


@app.route("/")
def index():
    # Your index.html already fetches /api/robots via JS
    return render_template("index.html")


@app.route("/api/robots")
def api_robots():
    if not LAPTOP_API:
        return jsonify({"error": "LAPTOP_API env var not set on Render"}), 500

    try:
        r = requests.get(f"{LAPTOP_API}/api/robots", timeout=4)
        data = r.json()
    except Exception as e:
        return jsonify({"error": "Could not reach laptop API", "details": str(e)}), 502

    robots = []

    # Case 1: laptop returns dict like {"R1":"No data","R2":"..."}
    if isinstance(data, dict):
        for rid, name in ID_MAP.items():
            status = data.get(rid, "No data")
            robots.append({
                "robot_id": name,
                "robot_name": name,
                "ping_count": 0,
                "last_seen": None,
                "last_data": status
            })
        return jsonify(robots)

    # Case 2: laptop returns list of dicts already
    if isinstance(data, list):
        # Convert robot_id if needed (R1 -> Pink Panther)
        out = []
        for r in data:
            rid = r.get("robot_id")
            name = ID_MAP.get(rid, rid)
            out.append({
                "robot_id": name,
                "robot_name": name,
                "ping_count": r.get("ping_count", 0),
                "last_seen": r.get("last_seen"),
                "last_data": r.get("last_data", "")
            })
        return jsonify(out)

    # Fallback
    return jsonify([])


@app.route("/api/command", methods=["POST"])
def api_command():
    """
    Called by your UI buttons.
    Forwards command to laptop API.
    """
    if not LAPTOP_API:
        return jsonify({"status": "error", "error": "LAPTOP_API not set"}), 500

    data = request.get_json(force=True)
    ui_robot_name = data.get("robot_id")
    command = data.get("command")

    if not ui_robot_name or not command:
        return jsonify({"status": "error", "error": "Missing robot_id or command"}), 400

    # Convert "Pink Panther" -> "R1"
    rid = NAME_TO_ID.get(ui_robot_name)
    if not rid:
        return jsonify({"status": "error", "error": "Unknown robot"}), 400

    try:
        # Forward to laptop
        r = requests.post(
            f"{LAPTOP_API}/api/command",
            json={"robot_id": rid, "command": command},
            timeout=4
        )
        if r.ok:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "details": r.text}), 500
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 502


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

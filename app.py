from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
lines = []  # store pyramid lines

@app.route('/send-data', methods=['POST'])
def receive_data():
    data = request.json
    if "line" in data:
        lines.append(data["line"])
    return jsonify({"status": "ok"})

@app.route('/')
def show_mario():
    # render pyramid lines on the homepage
    html = "<h1>Mario (more)</h1><pre>{}</pre>".format("\n".join(lines))
    return render_template_string(html)

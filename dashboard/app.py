from flask import Flask, render_template, jsonify, send_file
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "../data/doorcam.db"))
IMAGE_DIR = os.path.expanduser("~")

# ---------------- DB HELPER ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

# API: last 50 events
@app.route("/api/events")
def api_events():
    if not os.path.exists(DB_PATH):
        return jsonify([])
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, device, type, timestamp, image FROM events ORDER BY id DESC LIMIT 50")
    rows = []
    for r in c.fetchall():
        row = dict(r)
        if row["image"]:
            row["image"] = os.path.basename(row["image"])
        rows.append(row)
    conn.close()
    return jsonify(rows)

# API: summary stats + daily chart data
@app.route("/api/stats")
def api_stats():
    if not os.path.exists(DB_PATH):
        return jsonify({"total": 0, "motion": 0, "button": 0, "daily": []})
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM events")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM events WHERE type='motion'")
    motion = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM events WHERE type='button'")
    button = c.fetchone()[0]
    c.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as count
        FROM events
        GROUP BY DATE(timestamp)
        ORDER BY day DESC
        LIMIT 7
    """)
    daily = [{"date": r["day"], "count": r["count"]} for r in c.fetchall()]
    conn.close()
    return jsonify({"total": total, "motion": motion, "button": button, "daily": daily})

# Serve captured images
@app.route("/image/<filename>")
def serve_image(filename):
    filepath = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype="image/jpeg")
    return "Not found", 404

# ---------------- RUN ----------------
if __name__ == "__main__":
    print("Dashboard running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

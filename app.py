from flask import Flask, Response, jsonify
from pathlib import Path
import json, os, time, hashlib
from datetime import date, timedelta

FILE = Path("/home/chris/time-report/report.json")
app = Flask(__name__)

def file_etag(p: Path) -> str:
    st = p.stat()
    raw = f"{st.st_mtime_ns}:{st.st_size}".encode()
    return hashlib.md5(raw).hexdigest()

@app.get("/report")
def report():
    if not FILE.exists():
        return jsonify(error="file not found", path=str(FILE)), 404

    data = FILE.read_text(encoding="utf-8")

    # If the file already contains JSON, return it as-is.
    try:
        payload = json.loads(data)
        body = json.dumps(payload)
    except json.JSONDecodeError:
        # Otherwise wrap the text in a JSON object.
        payload = {"content": data}
        body = json.dumps(payload)

    etag = file_etag(FILE)
    resp = Response(body, mimetype="application/json; charset=utf-8")
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.get("/")
def root():
    return jsonify(ok=True, endpoint="/report")

@app.get("/current")
def current():
    # Ensure the report file exists and has the expected structure
    if FILE.exists():
        try:
            data = json.loads(FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    days = data.get("days")
    weeks = data.get("weeks")
    months = data.get("months")

    today = date.today()
    day_key = today.isoformat()

    # Weeks are Sunday..Saturday
    days_since_sunday = (today.weekday() + 1) % 7
    week_start = today - timedelta(days=days_since_sunday)
    week_end = week_start + timedelta(days=6)
    week_key = f"{week_start.isoformat()}..{week_end.isoformat()}"
    month_key = f"{today.year:04d}-{today.month:02d}"

    if day_key not in days:
        days[day_key] = "0h0m"

    if week_key not in weeks:
        weeks[week_key] = "0h0m"

    if month_key not in months:
        months[month_key] = "0h0m"

    payload = {
        "day": {day_key: days[day_key]},
        "week": {week_key: weeks[week_key]},
        "month": {month_key: months[month_key]},
    }

    resp = Response(json.dumps(payload), mimetype="application/json; charset=utf-8")
    resp.headers["Cache-Control"] = "no-store"
    return resp

if __name__ == "__main__":
    # Listen on LAN
    app.run(host="0.0.0.0", port=8000)

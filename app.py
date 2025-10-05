from flask import Flask, Response, jsonify
from pathlib import Path
import json, os, time, hashlib

FILE = Path("/home/chris/midi_recordings/time_report.txt")
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

if __name__ == "__main__":
    # Listen on LAN
    app.run(host="0.0.0.0", port=8000)

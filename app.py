import os
import json
import time
import random
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# --- PASTIKAN FAIL NI ADA KAT GITHUB ---
def load_json(file):
    if os.path.exists(file):
        with open(file, 'r') as f: return json.load(f)
    return {}

# --- LOGIK DATA ---
@app.route('/api/data')
def get_data():
    try:
        ts = int(time.time() * 1000)
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts=1774028458718}"
        r = requests.get(url, timeout=5)
        return jsonify(r.json())
    except:
        return jsonify({"status":"error"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    uid = data.get('id')
    users = load_json('users.json')
    if uid in users:
        return jsonify({"status": "valid", "name": users[uid]['name'], "expired": users[uid]['expired']})
    return jsonify({"status": "invalid"})

@app.route('/')
def index():
    return "<h1>SERVER LIVE ✅</h1><p>Gunakan ID Akses anda di app.</p>"

if __name__ == '__main__':
    # INI BAHAGIAN PALING PENTING UNTUK RENDER
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import os
import json
import time
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# --- LOAD USER DATABASE ---
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f: return json.load(f)
    return {}

# --- UI HTML + JS (CYBERPUNK) ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MySGAME V6 PRO</title>
    <style>
        body { background: #050505; color: #00ffcc; font-family: 'Courier New', monospace; text-align: center; padding: 20px; }
        .card { border: 1px solid #00ffcc; padding: 20px; border-radius: 10px; background: #000; box-shadow: 0 0 15px #00ffcc33; max-width: 450px; margin: auto; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #111; border: 1px solid #333; color: #0f0; text-align: center; }
        button { width: 100%; padding: 12px; background: #00ffcc; color: #000; border: none; font-weight: bold; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.75rem; }
        th, td { border: 1px solid #222; padding: 8px; }
        .win { color: #0f0; } .lose { color: #f00; }
    </style>
</head>
<body>
    <div id="login-ui" class="card">
        <h2>TERMINAL LOGIN</h2>
        <input type="text" id="user-id" placeholder="MASUKKAN ID AKSES">
        <button onclick="login()">LOGIN SYSTEM</button>
    </div>

    <div id="main-ui" class="card" style="display:none;">
        <h3 id="welcome"></h3>
        <table>
            <thead><tr><th>PERIOD</th><th>PRED</th><th>RESULT</th><th>STATUS</th></tr></thead>
            <tbody id="list"></tbody>
        </table>
        <p id="expiry" style="font-size: 0.6rem; color: #444; margin-top: 10px;"></p>
    </div>

    <script>
        async function login() {
            const id = document.getElementById('user-id').value;
            const r = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            });
            const d = await r.json();
            if(d.status === "valid") {
                document.getElementById('login-ui').style.display = 'none';
                document.getElementById('main-ui').style.display = 'block';
                document.getElementById('welcome').innerText = "USER: " + d.name;
                document.getElementById('expiry').innerText = "EXPIRED: " + d.expired;
                // Lepas login, sistem start tarik data
                setInterval(fetchData, 5000); 
                fetchData();
            } else { alert("ID TIDAK SAH!"); }
        }

        async function fetchData() {
            const r = await fetch('/api/data');
            const d = await r.json();
            if(d.data) {
                let html = "";
                // Tunjuk 5 data terbaru
                d.data.list.slice(0, 5).forEach(i => {
                    html += `<tr><td>${i.issue}</td><td>AI SCAN</td><td>${i.number}</td><td>OK</td></tr>`;
                });
                document.getElementById('list').innerHTML = html;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    uid = data.get('id')
    users = load_users()
    if uid in users:
        return jsonify({"status": "valid", "name": users[uid]['name'], "expired": users[uid]['expired']})
    return jsonify({"status": "invalid"})

@app.route('/api/data')
def api_data():
    try:
        ts = int(time.time() * 1000)
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts=1774028458718}"
        r = requests.get(url, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({"status": "error"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

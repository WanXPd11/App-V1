import os
import time
import json
import random
import requests
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request

# --- SETUP ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

# --- GLOBAL STATE ---
state = {
    "history": [],
    "last_issue": None,
    "win": 0,
    "lose": 0,
    "streak": 0
}

# --- LOGIK SISTEM ---
def get_random_ua():
    try:
        if os.path.exists('user_agents.txt'):
            with open('user_agents.txt', 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                return random.choice(lines)
    except:
        pass
    return "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"

def check_auth(user_id):
    try:
        if not os.path.exists('users.json'):
            return {"status": "error", "msg": "Database users.json hilang!"}
            
        with open('users.json', 'r') as f:
            users = json.load(f)
            
        if user_id in users:
            user_data = users[user_id]
            # Tukar string tarikh kepada objek datetime
            expiry = datetime.strptime(user_data['expired'], '%Y-%m-%d')
            now = datetime.now()
            
            if now < expiry:
                return {"status": "valid", "name": user_data['name'], "expired": user_data['expired']}
            else:
                return {"status": "expired", "name": user_data['name']}
        return {"status": "invalid"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

def get_bs(n):
    return "BIG" if int(n) >= 5 else "SMALL"

# --- ROUTES ---
@app.route('/api/login', methods=['POST'])
def do_login():
    data = request.json
    user_id = data.get('id')
    return jsonify(check_auth(user_id))

@app.route('/api/data')
def api_data():
    global state
    try:
        ts = int(time.time() * 1000)
        headers = {"User-Agent": get_random_ua(), "Accept": "application/json"}
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts={ts}"
        
        r = requests.get(url, headers=headers, timeout=10)
        res = r.json()
        
        all_list = res["data"]["list"]
        latest_now = all_list[0]
        issue_now = str(latest_now["issue"])
        num_now = int(latest_now["number"])
        size_now = get_bs(num_now)

        if issue_now != state["last_issue"]:
            for item in state["history"]:
                if item["issue"] == issue_now and item["status"] == "WAIT":
                    item["result"] = f"{size_now} ({num_now})"
                    if item["pred"] == size_now:
                        state["win"] += 1
                        state["streak"] = (state["streak"] + 1) if state["streak"] >= 0 else 1
                        item["status"] = "WIN"
                    else:
                        state["lose"] += 1
                        state["streak"] = (state["streak"] - 1) if state["streak"] <= 0 else -1
                        item["status"] = "LOSE"

            next_issue = str(int(issue_now) + 1)
            # Logik AI Shadow V6
            r1 = get_bs(all_list[0]["number"])
            r2 = get_bs(all_list[1]["number"])
            pred = r1 if r1 == r2 else ("SMALL" if r1 == "BIG" else "BIG")
            
            state["history"].insert(0, {
                "issue": next_issue, "pred": pred, "ai": "SHADOW-V6",
                "result": "WAIT...", "status": "WAIT"
            })
            if len(state["history"]) > 10: state["history"].pop()
            state["last_issue"] = issue_now

        return jsonify({"status": "success", "history": state["history"], "win": state["win"], "lose": state["lose"], "streak": state["streak"]})
    except:
        return jsonify({"status": "error"})

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

# --- UI HTML ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MySGAME PRO V6</title>
    <style>
        body { background: #050505; color: #00ffcc; font-family: 'Courier New', monospace; text-align: center; padding: 20px; }
        .card { border: 1px solid #00ffcc; padding: 20px; border-radius: 10px; background: #000; box-shadow: 0 0 15px #00ffcc33; max-width: 450px; margin: auto; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #111; border: 1px solid #333; color: #0f0; text-align: center; }
        button { width: 100%; padding: 12px; background: #00ffcc; color: #000; border: none; font-weight: bold; cursor: pointer; }
        .stats { display: flex; justify-content: space-around; margin: 15px 0; font-size: 0.8rem; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.75rem; }
        th, td { border: 1px solid #222; padding: 8px; }
        .win { color: #0f0; } .lose { color: #f00; } .wait { color: #ff0; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.4; } }
    </style>
</head>
<body>
    <div id="login-ui" class="card">
        <h2>TERMINAL LOGIN</h2>
        <p style="font-size: 0.7rem; color: #666;">SERVER: ASIA-WINGO-1M</p>
        <input type="text" id="user-id" placeholder="MASUKKAN ID AKSES">
        <button onclick="login()">LOGIN SYSTEM</button>
    </div>

    <div id="main-ui" class="card" style="display:none;">
        <h3 id="welcome-msg">WELCOME</h3>
        <div class="stats">
            <div>WIN: <span id="w" class="win">0</span></div>
            <div>LOSE: <span id="l" class="lose">0</span></div>
            <div>STREAK: <span id="s">0</span></div>
        </div>
        <table>
            <thead><tr><th>PERIOD</th><th>PRED</th><th>RESULT</th><th>STATUS</th></tr></thead>
            <tbody id="list"></tbody>
        </table>
        <p id="expiry-msg" style="font-size: 0.6rem; color: #444; margin-top: 10px;"></p>
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
                document.getElementById('welcome-msg').innerText = "USER: " + d.name;
                document.getElementById('expiry-msg').innerText = "LICENSE EXPIRED: " + d.expired;
                setInterval(fetchData, 4000); fetchData();
            } else if(d.status === "expired") { alert("ID EXPIRED! Sila renew."); }
            else { alert("ID TIDAK SAH!"); }
        }

        async function fetchData() {
            const r = await fetch('/api/data');
            const d = await r.json();
            if(d.status === "success") {
                document.getElementById('w').innerText = d.win;
                document.getElementById('l').innerText = d.lose;
                document.getElementById('s').innerText = d.streak;
                let html = "";
                d.history.forEach(i => {
                    html += `<tr>
                        <td>${i.issue.slice(-4)}</td>
                        <td style="color:yellow">${i.pred}</td>
                        <td>${i.result}</td>
                        <td class="${i.status.toLowerCase()}">${i.status}</td>
                    </tr>`;
                });
                document.getElementById('list').innerHTML = html;
            }
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

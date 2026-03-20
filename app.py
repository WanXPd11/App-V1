import os
import json
import time
import requests
import random
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# --- DATABASE USERS & AGENTS ---
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

def get_ua():
    if os.path.exists('user_agents.txt'):
        with open('user_agents.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
            return random.choice(lines) if lines else "Mozilla/5.0"
    return "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"

# --- UI HTML (CYBERPUNK V6.1) ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MSYGAME PREDICTION</title>
    <style>
        body { background: #000; color: #00ffcc; font-family: 'Courier New', monospace; text-align: center; padding: 10px; margin: 0; }
        .card { border: 2px solid #00ffcc; padding: 15px; border-radius: 5px; background: rgba(0, 255, 204, 0.05); max-width: 380px; margin: 20px auto; box-shadow: 0 0 20px #00ffcc44; }
        
        /* TAJUK KECIL KAT ATAS */
        .header-title { font-size: 1.2rem; font-weight: bold; letter-spacing: 2px; color: #fff; text-shadow: 0 0 10px #00ffcc; margin-bottom: 5px; }
        .sub-header { font-size: 0.6rem; color: #00ffcc; margin-bottom: 15px; border-bottom: 1px solid #00ffcc; padding-bottom: 5px; opacity: 0.7; }

        input { width: 85%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #00ffcc; color: #fff; text-align: center; outline: none; }
        button { width: 92%; padding: 12px; background: #00ffcc; color: #000; font-weight: bold; border: none; cursor: pointer; transition: 0.3s; text-transform: uppercase; }
        button:hover { background: #fff; box-shadow: 0 0 15px #fff; }

        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.7rem; }
        th { background: #00ffcc; color: #000; padding: 8px; text-transform: uppercase; }
        td { border: 1px solid #1a1a1a; padding: 10px; background: #080808; }
        
        .big { color: #ff0055; font-weight: bold; } 
        .small { color: #00ffcc; font-weight: bold; }
        .pred-box { color: #ffff00; font-size: 0.8rem; font-weight: bold; text-shadow: 0 0 5px #ffff00; }
        
        #user-info { font-size: 0.7rem; color: #888; margin-top: 10px; }
    </style>
</head>
<body>
    <div id="login-ui" class="card">
        <div class="header-title">MSYGAME PREDICTION</div>
        <div class="sub-header">AI ANALYSIS TERMINAL V6.1</div>
        <input type="text" id="uid" placeholder="ENTER ACCESS ID">
        <button onclick="doLogin()">ACCESS SYSTEM</button>
    </div>

    <div id="main-ui" class="card" style="display:none;">
        <div class="header-title" style="font-size: 1rem;">MSYGAME PREDICTION</div>
        <div id="user-info"></div>
        <table>
            <thead>
                <tr>
                    <th>PERIOD</th>
                    <th>PREDICTION</th>
                    <th>RESULT</th>
                </tr>
            </thead>
            <tbody id="list">
                <tr><td colspan="3">SCANNING DATABASE...</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        async function doLogin() {
            const id = document.getElementById('uid').value;
            try {
                const r = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: id})
                });
                const d = await r.json();
                if(d.status === "valid") {
                    document.getElementById('login-ui').style.display = 'none';
                    document.getElementById('main-ui').style.display = 'block';
                    document.getElementById('user-info').innerText = "OPERATOR: " + d.name + " | EXP: " + d.expired;
                    setInterval(fetchData, 4000); 
                    fetchData();
                } else { alert("INVALID ID!"); }
            } catch(e) { alert("CONNECTION ERROR!"); }
        }

        async function fetchData() {
            try {
                const r = await fetch('/api/data');
                const d = await r.json();
                if(d.status === "success" && d.history.length > 0) {
                    let html = "";
                    d.history.forEach(i => {
                        let resClass = i.result.includes("BIG") ? "big" : "small";
                        html += `<tr>
                            <td>${i.issue}</td>
                            <td class="pred-box">${i.pred}</td>
                            <td class="${resClass}">${i.result}</td>
                        </tr>`;
                    });
                    document.getElementById('list').innerHTML = html;
                }
            } catch(e) {}
        }
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---
@app.route('/')
def index(): return render_template_string(HTML_CODE)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    uid = data.get('id')
    users = load_json('users.json')
    if uid in users:
        return jsonify({"status": "valid", "name": users[uid]['name'], "expired": users[uid]['expired']})
    return jsonify({"status": "invalid"})

@app.route('/api/data')
def api_data():
    try:
        # Guna link API utama
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts=1774028458718"
        {int(time.time()*1000)}"
        headers = {"User-Agent": get_ua()}
        r = requests.get(url, headers=headers, timeout=10)
        res = r.json()
        
        raw_list = res["data"]["list"]
        history = []
        
        for i in range(6):
            item = raw_list[i]
            num = int(item["number"])
            size = "BIG" if num >= 5 else "SMALL"
            
            # Logik AI SHADOW: Lawan trend sebelumnya
            pred = "BIG" if size == "SMALL" else "SMALL"
            
            history.append({
                "issue": str(item["issue"])[-4:],
                "pred": pred,
                "result": f"{size} ({num})"
            })
            
        return jsonify({"status": "success", "history": history})
    except:
        return jsonify({"status": "error", "history": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

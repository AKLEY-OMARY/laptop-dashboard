from flask import Flask, jsonify, render_template_string, request
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>🖥️ Laptop Monitor</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial; background: #0d1117; color: #c9d1d9; padding: 30px; }
    h1 { color: #58a6ff; margin-bottom: 5px; }
    p.sub { color: #8b949e; margin-bottom: 25px; font-size: 0.9em; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
    .label { color: #8b949e; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; }
    .value { font-size: 2em; font-weight: bold; color: #00ff88; margin: 8px 0; }
    .bar-bg { background: #21262d; border-radius: 6px; height: 8px; }
    .bar { background: linear-gradient(90deg, #00ff88, #58a6ff); height: 8px; border-radius: 6px; transition: width 0.6s ease; }
    .status { display: inline-block; width: 10px; height: 10px; background: #00ff88; border-radius: 50%; margin-right: 6px; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  </style>
  <script>
    async function fetchStats() {
      try {
        const res = await fetch('/stats');
        const d = await res.json();
        if (!d.cpu && d.cpu !== 0) return;
        document.getElementById('cpu-val').innerText = d.cpu + '%';
        document.getElementById('ram-val').innerText = d.ram + '%';
        document.getElementById('disk-val').innerText = d.disk + '%';
        document.getElementById('host-val').innerText = d.hostname;
        document.getElementById('uptime-val').innerText = d.uptime;
        document.getElementById('cpu-bar').style.width = d.cpu + '%';
        document.getElementById('ram-bar').style.width = d.ram + '%';
        document.getElementById('disk-bar').style.width = d.disk + '%';
        document.getElementById('time').innerText = new Date().toLocaleTimeString();
      } catch(e) {}
    }
    setInterval(fetchStats, 2000);
    fetchStats();
  </script>
</head>
<body>
  <h1>🖥️ Real-Time Laptop Monitor</h1>
  <p class="sub"><span class="status"></span>Live · Last updated: <span id="time">connecting...</span></p>
  <div class="grid">
    <div class="card">
      <div class="label">Hostname</div>
      <div class="value" style="font-size:1.2em" id="host-val">-</div>
    </div>
    <div class="card">
      <div class="label">CPU Usage</div>
      <div class="value" id="cpu-val">-</div>
      <div class="bar-bg"><div class="bar" id="cpu-bar" style="width:0%"></div></div>
    </div>
    <div class="card">
      <div class="label">RAM Usage</div>
      <div class="value" id="ram-val">-</div>
      <div class="bar-bg"><div class="bar" id="ram-bar" style="width:0%"></div></div>
    </div>
    <div class="card">
      <div class="label">Disk Usage</div>
      <div class="value" id="disk-val">-</div>
      <div class="bar-bg"><div class="bar" id="disk-bar" style="width:0%"></div></div>
    </div>
    <div class="card">
      <div class="label">Uptime</div>
      <div class="value" style="font-size:1em" id="uptime-val">-</div>
    </div>
  </div>
</body>
</html>
"""

latest_stats = {}

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/stats')
def stats():
    return jsonify(latest_stats)

@app.route('/update', methods=['POST'])
def update():
    global latest_stats
    latest_stats = request.get_json()
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

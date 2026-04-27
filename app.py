from flask import Flask, jsonify, render_template_string, request
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🖥️ Laptop Monitor</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: 'Rajdhani', sans-serif;
      background: #000;
      color: #fff;
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* Animated background */
    .bg {
      position: fixed; top: 0; left: 0;
      width: 100%; height: 100%;
      background: radial-gradient(ellipse at top, #0a0a2e 0%, #000 60%);
      z-index: -2;
    }
    .bg::before {
      content: '';
      position: absolute; top: 0; left: 0;
      width: 100%; height: 100%;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%230066ff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
      z-index: -1;
    }

    /* Grid lines effect */
    .grid-lines {
      position: fixed; top: 0; left: 0;
      width: 100%; height: 100%;
      background-image: 
        linear-gradient(rgba(0,100,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,100,255,0.03) 1px, transparent 1px);
      background-size: 50px 50px;
      z-index: -1;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 30px 20px;
    }

    /* Header */
    header {
      text-align: center;
      margin-bottom: 40px;
      position: relative;
    }

    .header-badge {
      display: inline-block;
      background: rgba(0,100,255,0.1);
      border: 1px solid rgba(0,100,255,0.3);
      border-radius: 20px;
      padding: 5px 15px;
      font-size: 0.75em;
      color: #4488ff;
      letter-spacing: 3px;
      text-transform: uppercase;
      margin-bottom: 15px;
    }

    h1 {
      font-family: 'Orbitron', monospace;
      font-size: 2.5em;
      font-weight: 900;
      background: linear-gradient(135deg, #fff 0%, #4488ff 50%, #00ffcc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: 3px;
      margin-bottom: 10px;
    }

    .subtitle {
      color: #4488ff;
      font-size: 1em;
      letter-spacing: 2px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }

    .live-dot {
      width: 8px; height: 8px;
      background: #00ff88;
      border-radius: 50%;
      animation: pulse 1.5s infinite;
      box-shadow: 0 0 10px #00ff88;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.8); }
    }

    /* Cards grid */
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }

    .card {
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px;
      padding: 25px;
      position: relative;
      overflow: hidden;
      transition: transform 0.3s, border-color 0.3s;
      backdrop-filter: blur(10px);
    }

    .card:hover {
      transform: translateY(-3px);
      border-color: rgba(0,100,255,0.4);
    }

    .card::before {
      content: '';
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 2px;
      background: linear-gradient(90deg, transparent, #4488ff, transparent);
      opacity: 0.6;
    }

    .card-icon {
      font-size: 2em;
      margin-bottom: 10px;
      display: block;
    }

    .card-label {
      font-size: 0.75em;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #4488ff;
      margin-bottom: 8px;
    }

    .card-value {
      font-family: 'Orbitron', monospace;
      font-size: 2.8em;
      font-weight: 700;
      color: #fff;
      line-height: 1;
      margin-bottom: 15px;
    }

    .card-value.hostname {
      font-size: 1.4em;
      color: #00ffcc;
    }

    .card-value.uptime-val {
      font-size: 1.2em;
      color: #ffaa00;
    }

    /* Progress bar */
    .bar-container {
      margin-top: 10px;
    }

    .bar-info {
      display: flex;
      justify-content: space-between;
      font-size: 0.8em;
      color: #666;
      margin-bottom: 6px;
    }

    .bar-bg {
      background: rgba(255,255,255,0.05);
      border-radius: 10px;
      height: 6px;
      overflow: hidden;
    }

    .bar {
      height: 100%;
      border-radius: 10px;
      transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
    }

    .bar-cpu { background: linear-gradient(90deg, #4488ff, #00ffcc); }
    .bar-ram { background: linear-gradient(90deg, #ff4488, #ffaa00); }
    .bar-disk { background: linear-gradient(90deg, #aa44ff, #4488ff); }

    .bar::after {
      content: '';
      position: absolute;
      top: 0; right: 0;
      width: 4px; height: 100%;
      background: rgba(255,255,255,0.8);
      border-radius: 10px;
      box-shadow: 0 0 8px rgba(255,255,255,0.8);
    }

    /* Status bar */
    .status-bar {
      background: rgba(255,255,255,0.02);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 12px;
      padding: 15px 25px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 10px;
    }

    .status-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85em;
      color: #888;
    }

    .status-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: #00ff88;
      box-shadow: 0 0 6px #00ff88;
    }

    /* Glow effects */
    .glow-blue { box-shadow: 0 0 30px rgba(68,136,255,0.1); }
    .glow-green { box-shadow: 0 0 30px rgba(0,255,136,0.1); }

    /* Warning colors */
    .warn { color: #ffaa00 !important; }
    .danger { color: #ff4444 !important; }
  </style>
  <script>
    async function fetchStats() {
      try {
        const res = await fetch('/stats');
        const d = await res.json();
        if (!d.cpu && d.cpu !== 0) return;

        // CPU
        const cpu = d.cpu;
        document.getElementById('cpu-val').innerText = cpu + '%';
        document.getElementById('cpu-bar').style.width = cpu + '%';
        const cpuEl = document.getElementById('cpu-val');
        cpuEl.className = 'card-value' + (cpu > 80 ? ' danger' : cpu > 60 ? ' warn' : '');

        // RAM
        const ram = d.ram;
        document.getElementById('ram-val').innerText = ram + '%';
        document.getElementById('ram-bar').style.width = ram + '%';

        // Disk
        const disk = d.disk;
        document.getElementById('disk-val').innerText = disk + '%';
        document.getElementById('disk-bar').style.width = disk + '%';

        // Others
        document.getElementById('host-val').innerText = d.hostname;
        document.getElementById('uptime-val').innerText = d.uptime;
        document.getElementById('time').innerText = new Date().toLocaleTimeString();
        document.getElementById('update-time').innerText = new Date().toLocaleTimeString();
      } catch(e) {}
    }
    setInterval(fetchStats, 2000);
    fetchStats();
  </script>
</head>
<body>
  <div class="bg"></div>
  <div class="grid-lines"></div>

  <div class="container">
    <header>
      <div class="header-badge">System Monitor v1.0</div>
      <h1>LAPTOP MONITOR</h1>
      <div class="subtitle">
        <div class="live-dot"></div>
        LIVE · Last updated: <span id="time">connecting...</span>
      </div>
    </header>

    <div class="grid">
      <!-- Hostname -->
      <div class="card glow-green">
        <span class="card-icon">💻</span>
        <div class="card-label">Hostname</div>
        <div class="card-value hostname" id="host-val">-</div>
      </div>

      <!-- Uptime -->
      <div class="card">
        <span class="card-icon">⏱️</span>
        <div class="card-label">System Uptime</div>
        <div class="card-value uptime-val" id="uptime-val">-</div>
      </div>

      <!-- CPU -->
      <div class="card glow-blue">
        <span class="card-icon">⚡</span>
        <div class="card-label">CPU Usage</div>
        <div class="card-value" id="cpu-val">-</div>
        <div class="bar-container">
          <div class="bar-info"><span>0%</span><span>100%</span></div>
          <div class="bar-bg">
            <div class="bar bar-cpu" id="cpu-bar" style="width:0%"></div>
          </div>
        </div>
      </div>

      <!-- RAM -->
      <div class="card">
        <span class="card-icon">🧠</span>
        <div class="card-label">RAM Usage</div>
        <div class="card-value" id="ram-val">-</div>
        <div class="bar-container">
          <div class="bar-info"><span>0%</span><span>100%</span></div>
          <div class="bar-bg">
            <div class="bar bar-ram" id="ram-bar" style="width:0%"></div>
          </div>
        </div>
      </div>

      <!-- Disk -->
      <div class="card">
        <span class="card-icon">💾</span>
        <div class="card-label">Disk Usage</div>
        <div class="card-value" id="disk-val">-</div>
        <div class="bar-container">
          <div class="bar-info"><span>0%</span><span>100%</span></div>
          <div class="bar-bg">
            <div class="bar bar-disk" id="disk-bar" style="width:0%"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Status bar -->
    <div class="status-bar">
      <div class="status-item">
        <div class="status-dot"></div>
        System Online
      </div>
      <div class="status-item">
        🔄 Auto-refresh every 2s
      </div>
      <div class="status-item">
        🕐 <span id="update-time">--:--:--</span>
      </div>
      <div class="status-item">
        ☁️ Hosted on Railway
      </div>
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

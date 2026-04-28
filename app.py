from flask import Flask, jsonify, render_template_string, request
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>System Monitor</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
  <style>
    :root {
      --blue: #4f8eff; --cyan: #00e5ff; --green: #00ff9d;
      --purple: #b44fff; --orange: #ff9d00; --red: #ff4f4f;
      --dark: #060810; --card: rgba(255,255,255,0.03); --border: rgba(255,255,255,0.07);
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'Inter',sans-serif; background:var(--dark); color:#fff; min-height:100vh; overflow-x:hidden; }

    .bg-animate {
      position:fixed; inset:0; z-index:-1;
      background:
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(79,142,255,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(180,79,255,0.06) 0%, transparent 60%),
        #060810;
    }
    .grid-overlay {
      position:fixed; inset:0; z-index:-1;
      background-image: linear-gradient(rgba(79,142,255,0.025) 1px,transparent 1px), linear-gradient(90deg,rgba(79,142,255,0.025) 1px,transparent 1px);
      background-size:60px 60px;
    }
    .particles { position:fixed; inset:0; z-index:-1; overflow:hidden; }
    .particle { position:absolute; border-radius:50%; opacity:0; animation:float linear infinite; }
    @keyframes float { 0%{transform:translateY(100vh);opacity:0} 10%{opacity:0.6} 90%{opacity:0.3} 100%{transform:translateY(-100px);opacity:0} }

    .container { max-width:1300px; margin:0 auto; padding:40px 24px; }

    /* Header */
    header { text-align:center; margin-bottom:50px; }
    .badge {
      display:inline-flex; align-items:center; gap:8px;
      background:rgba(79,142,255,0.1); border:1px solid rgba(79,142,255,0.25);
      border-radius:100px; padding:6px 18px;
      font-size:0.7em; letter-spacing:3px; text-transform:uppercase; color:var(--blue); margin-bottom:20px;
    }
    .badge-dot { width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green); animation:pulse 1.5s infinite; }
    h1 {
      font-family:'Orbitron',monospace; font-size:clamp(1.8em,5vw,3.5em); font-weight:900; letter-spacing:6px;
      background:linear-gradient(135deg,#fff 0%,var(--blue) 40%,var(--cyan) 70%,var(--green) 100%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:12px;
    }
    .tagline { color:rgba(255,255,255,0.35); font-size:0.9em; letter-spacing:2px; margin-bottom:16px; }
    .live-status { display:inline-flex; align-items:center; gap:8px; font-size:0.8em; color:var(--green); font-family:'Orbitron',monospace; letter-spacing:2px; }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.3;transform:scale(0.7)} }

    /* Mini cards */
    .top-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:20px; }
    .mini-card {
      background:var(--card); border:1px solid var(--border); border-radius:16px; padding:20px;
      display:flex; align-items:center; gap:16px; transition:all 0.3s; position:relative; overflow:hidden;
    }
    .mini-card:hover { transform:translateY(-4px); border-color:rgba(79,142,255,0.3); box-shadow:0 20px 40px rgba(0,0,0,0.3); }
    .mini-icon { width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.4em; flex-shrink:0; }
    .icon-blue { background:rgba(79,142,255,0.15); } .icon-green { background:rgba(0,255,157,0.1); }
    .icon-purple { background:rgba(180,79,255,0.1); } .icon-orange { background:rgba(255,157,0,0.1); }
    .mini-label { font-size:0.7em; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.35); margin-bottom:4px; }
    .mini-value { font-family:'Orbitron',monospace; font-size:1.2em; font-weight:700; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

    /* Gauge cards */
    .gauge-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(360px,1fr)); gap:20px; margin-bottom:20px; }
    .gauge-card {
      background:var(--card); border:1px solid var(--border); border-radius:20px; padding:28px;
      position:relative; overflow:hidden; transition:all 0.3s;
    }
    .gauge-card:hover { transform:translateY(-4px); box-shadow:0 24px 50px rgba(0,0,0,0.4); }
    .gauge-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--accent),transparent); }
    .gauge-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
    .gauge-title { display:flex; align-items:center; gap:10px; font-size:0.75em; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.4); }
    .gauge-percent { font-family:'Orbitron',monospace; font-size:2.5em; font-weight:900; }

    /* SVG Circle with emoji inside */
    .circle-wrap { display:flex; justify-content:center; margin-bottom:20px; position:relative; }
    .circle-emoji {
      position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
      font-size:2.2em; line-height:1;
      filter:drop-shadow(0 0 12px rgba(255,255,255,0.3));
      animation:float-icon 3s ease-in-out infinite;
    }
    @keyframes float-icon { 0%,100%{transform:translate(-50%,-50%) scale(1)} 50%{transform:translate(-50%,-54%) scale(1.08)} }

    .circle-bg { fill:none; stroke:rgba(255,255,255,0.05); stroke-width:10; }
    .circle-track { fill:none; stroke-width:10; stroke-linecap:round; transition:stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1); }

    /* Bar */
    .bar-wrap { margin-top:8px; }
    .bar-labels { display:flex; justify-content:space-between; font-size:0.72em; color:rgba(255,255,255,0.2); margin-bottom:6px; }
    .bar-track { background:rgba(255,255,255,0.05); border-radius:100px; height:7px; overflow:hidden; }
    .bar-fill { height:100%; border-radius:100px; transition:width 0.8s cubic-bezier(0.4,0,0.2,1); position:relative; }
    .bar-fill::after { content:''; position:absolute; top:0; right:0; bottom:0; width:20px; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.4)); border-radius:100px; }
    .bar-cpu { background:linear-gradient(90deg,#4f8eff,#00e5ff); }
    .bar-ram { background:linear-gradient(90deg,#b44fff,#ff4f9d); }
    .bar-disk { background:linear-gradient(90deg,#ff9d00,#ff4f4f); }

    /* Graph section */
    .graph-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(380px,1fr)); gap:20px; margin-bottom:20px; }
    .graph-card {
      background:var(--card); border:1px solid var(--border); border-radius:20px; padding:24px;
      transition:all 0.3s;
    }
    .graph-card:hover { transform:translateY(-3px); border-color:rgba(79,142,255,0.2); }
    .graph-title { font-size:0.75em; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.35); margin-bottom:16px; display:flex; align-items:center; gap:8px; }
    .graph-canvas { width:100% !important; height:160px !important; }

    /* Footer */
    .footer-bar {
      background:var(--card); border:1px solid var(--border); border-radius:16px; padding:16px 24px;
      display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px;
    }
    .footer-item { display:flex; align-items:center; gap:8px; font-size:0.78em; color:rgba(255,255,255,0.3); }
    .footer-dot { width:6px; height:6px; border-radius:50%; }
    .dot-green { background:var(--green); box-shadow:0 0 6px var(--green); }
    .dot-blue { background:var(--blue); box-shadow:0 0 6px var(--blue); }

    .cpu-card { --accent:var(--blue); }
    .ram-card { --accent:var(--purple); }
    .disk-card { --accent:var(--orange); }
  </style>

  <script>
    // Particles
    window.addEventListener('load', () => {
      const c = document.querySelector('.particles');
      for (let i = 0; i < 30; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.cssText = `left:${Math.random()*100}%;width:${1+Math.random()*2}px;height:${1+Math.random()*2}px;background:${['#4f8eff','#00e5ff','#00ff9d','#b44fff'][Math.floor(Math.random()*4)]};animation-duration:${8+Math.random()*15}s;animation-delay:${Math.random()*10}s;`;
        c.appendChild(p);
      }
    });

    // Chart history
    const MAX = 30;
    const history = { cpu: Array(MAX).fill(0), ram: Array(MAX).fill(0), disk: Array(MAX).fill(0) };
    const labels = Array(MAX).fill('');

    let cpuChart, ramChart, diskChart;

    function makeChart(id, color, label) {
      const ctx = document.getElementById(id).getContext('2d');
      return new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: label,
            data: history[label.toLowerCase()],
            borderColor: color,
            backgroundColor: color.replace(')', ',0.08)').replace('rgb','rgba'),
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.4,
            fill: true,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 600 },
          plugins: { legend: { display: false } },
          scales: {
            x: { display: false },
            y: {
              min: 0, max: 100,
              grid: { color: 'rgba(255,255,255,0.04)' },
              ticks: { color: 'rgba(255,255,255,0.2)', font: { size: 10 }, callback: v => v + '%' }
            }
          }
        }
      });
    }

    window.addEventListener('load', () => {
      cpuChart  = makeChart('cpuChart',  'rgb(79,142,255)',  'Cpu');
      ramChart  = makeChart('ramChart',  'rgb(180,79,255)',  'Ram');
      diskChart = makeChart('diskChart', 'rgb(255,157,0)',   'Disk');
    });

    function pushHistory(key, val) {
      history[key].push(val);
      if (history[key].length > MAX) history[key].shift();
    }

    function setCircle(id, pct) {
      const el = document.getElementById(id);
      if (!el) return;
      const circ = 2 * Math.PI * 54;
      el.style.strokeDasharray = circ;
      el.style.strokeDashoffset = circ - (pct / 100) * circ;
    }

    function alertColor(val) {
      if (val >= 85) return '#ff4f4f';
      if (val >= 65) return '#ff9d00';
      return null;
    }

    async function fetchStats() {
      try {
        const res = await fetch('/stats');
        const d = await res.json();
        if (d.cpu === undefined) return;

        const cpu = d.cpu, ram = d.ram, disk = d.disk;

        // Mini cards
        document.getElementById('host-val').innerText = d.hostname || '-';
        document.getElementById('uptime-val').innerText = d.uptime || '-';
        document.getElementById('time').innerText = new Date().toLocaleTimeString();
        document.getElementById('footer-time').innerText = new Date().toLocaleTimeString();

        // CPU
        document.getElementById('cpu-pct').innerText = cpu + '%';
        document.getElementById('cpu-bar').style.width = cpu + '%';
        setCircle('cpu-circle', cpu);
        document.getElementById('cpu-pct').style.color = alertColor(cpu) || 'var(--cyan)';

        // RAM
        document.getElementById('ram-pct').innerText = ram + '%';
        document.getElementById('ram-bar').style.width = ram + '%';
        setCircle('ram-circle', ram);
        document.getElementById('ram-pct').style.color = alertColor(ram) || 'var(--purple)';

        // Disk
        document.getElementById('disk-pct').innerText = disk + '%';
        document.getElementById('disk-bar').style.width = disk + '%';
        setCircle('disk-circle', disk);
        document.getElementById('disk-pct').style.color = alertColor(disk) || 'var(--orange)';

        // Update charts
        pushHistory('cpu', cpu);
        pushHistory('ram', ram);
        pushHistory('disk', disk);
        if (cpuChart)  { cpuChart.data.datasets[0].data  = [...history.cpu];  cpuChart.update('none'); }
        if (ramChart)  { ramChart.data.datasets[0].data  = [...history.ram];  ramChart.update('none'); }
        if (diskChart) { diskChart.data.datasets[0].data = [...history.disk]; diskChart.update('none'); }

      } catch(e) {}
    }

    setInterval(fetchStats, 2000);
    fetchStats();
  </script>
</head>
<body>
  <div class="bg-animate"></div>
  <div class="particles"></div>
  <div class="grid-overlay"></div>

  <div class="container">
    <header>
      <div class="badge"><div class="badge-dot"></div> System Monitor</div>
      <h1>LIVE DASHBOARD</h1>
      <p class="tagline">Real-Time Laptop Performance Monitor</p>
      <div class="live-status"><div class="badge-dot"></div> LIVE · <span id="time">connecting...</span></div>
    </header>

    <!-- Mini cards -->
    <div class="top-row">
      <div class="mini-card">
        <div class="mini-icon icon-green">💻</div>
        <div><div class="mini-label">Hostname</div><div class="mini-value" id="host-val">-</div></div>
      </div>
      <div class="mini-card">
        <div class="mini-icon icon-orange">⏱️</div>
        <div><div class="mini-label">Uptime</div><div class="mini-value" id="uptime-val">-</div></div>
      </div>
      <div class="mini-card">
        <div class="mini-icon icon-blue">🐧</div>
        <div><div class="mini-label">Platform</div><div class="mini-value">Linux</div></div>
      </div>
      <div class="mini-card">
        <div class="mini-icon icon-purple">☁️</div>
        <div><div class="mini-label">Hosted On</div><div class="mini-value">Railway</div></div>
      </div>
    </div>

    <!-- Gauge cards -->
    <div class="gauge-row">

      <!-- CPU -->
      <div class="gauge-card cpu-card">
        <div class="gauge-header">
          <div class="gauge-title">⚡ CPU Usage</div>
          <div class="gauge-percent" id="cpu-pct" style="color:var(--cyan)">-</div>
        </div>
        <div class="circle-wrap">
          <svg width="150" height="150" viewBox="0 0 150 150">
            <circle class="circle-bg" cx="75" cy="75" r="54"/>
            <circle class="circle-track" id="cpu-circle" cx="75" cy="75" r="54"
              stroke="url(#gradCpu)" stroke-dasharray="339.3" stroke-dashoffset="339.3"
              transform="rotate(-90 75 75)"/>
            <defs>
              <linearGradient id="gradCpu" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#4f8eff"/>
                <stop offset="100%" stop-color="#00e5ff"/>
              </linearGradient>
            </defs>
          </svg>
          <div class="circle-emoji">⚡</div>
        </div>
        <div class="bar-wrap">
          <div class="bar-labels"><span>0%</span><span>50%</span><span>100%</span></div>
          <div class="bar-track"><div class="bar-fill bar-cpu" id="cpu-bar" style="width:0%"></div></div>
        </div>
      </div>

      <!-- RAM -->
      <div class="gauge-card ram-card">
        <div class="gauge-header">
          <div class="gauge-title">🧠 RAM Usage</div>
          <div class="gauge-percent" id="ram-pct" style="color:var(--purple)">-</div>
        </div>
        <div class="circle-wrap">
          <svg width="150" height="150" viewBox="0 0 150 150">
            <circle class="circle-bg" cx="75" cy="75" r="54"/>
            <circle class="circle-track" id="ram-circle" cx="75" cy="75" r="54"
              stroke="url(#gradRam)" stroke-dasharray="339.3" stroke-dashoffset="339.3"
              transform="rotate(-90 75 75)"/>
            <defs>
              <linearGradient id="gradRam" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#b44fff"/>
                <stop offset="100%" stop-color="#ff4f9d"/>
              </linearGradient>
            </defs>
          </svg>
          <div class="circle-emoji">🧠</div>
        </div>
        <div class="bar-wrap">
          <div class="bar-labels"><span>0%</span><span>50%</span><span>100%</span></div>
          <div class="bar-track"><div class="bar-fill bar-ram" id="ram-bar" style="width:0%"></div></div>
        </div>
      </div>

      <!-- Disk -->
      <div class="gauge-card disk-card">
        <div class="gauge-header">
          <div class="gauge-title">💾 Disk Usage</div>
          <div class="gauge-percent" id="disk-pct" style="color:var(--orange)">-</div>
        </div>
        <div class="circle-wrap">
          <svg width="150" height="150" viewBox="0 0 150 150">
            <circle class="circle-bg" cx="75" cy="75" r="54"/>
            <circle class="circle-track" id="disk-circle" cx="75" cy="75" r="54"
              stroke="url(#gradDisk)" stroke-dasharray="339.3" stroke-dashoffset="339.3"
              transform="rotate(-90 75 75)"/>
            <defs>
              <linearGradient id="gradDisk" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#ff9d00"/>
                <stop offset="100%" stop-color="#ff4f4f"/>
              </linearGradient>
            </defs>
          </svg>
          <div class="circle-emoji">💾</div>
        </div>
        <div class="bar-wrap">
          <div class="bar-labels"><span>0%</span><span>50%</span><span>100%</span></div>
          <div class="bar-track"><div class="bar-fill bar-disk" id="disk-bar" style="width:0%"></div></div>
        </div>
      </div>

    </div>

    <!-- Graphs -->
    <div class="graph-row">
      <div class="graph-card">
        <div class="graph-title">📈 CPU History</div>
        <canvas id="cpuChart" class="graph-canvas"></canvas>
      </div>
      <div class="graph-card">
        <div class="graph-title">📊 RAM History</div>
        <canvas id="ramChart" class="graph-canvas"></canvas>
      </div>
      <div class="graph-card">
        <div class="graph-title">📉 Disk History</div>
        <canvas id="diskChart" class="graph-canvas"></canvas>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer-bar">
      <div class="footer-item"><div class="footer-dot dot-green"></div> System Online</div>
      <div class="footer-item"><div class="footer-dot dot-blue"></div> Auto-refresh every 2s</div>
      <div class="footer-item">🕐 Last update: <span id="footer-time">--:--:--</span></div>
      <div class="footer-item">☁️ Deployed on Railway Cloud</div>
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

import psutil, requests, socket, time, subprocess

RAILWAY_URL = "https://web-production-bc74a.up.railway.app"

def get_uptime():
    result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
    return result.stdout.strip()

print(f"📡 Sending stats to {RAILWAY_URL}")
print("Press Ctrl+C to stop\n")

while True:
    stats = {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "hostname": socket.gethostname(),
        "uptime": get_uptime()
    }
    try:
        requests.post(f"{RAILWAY_URL}/update", json=stats, timeout=10)
        print(f"✅ CPU: {stats['cpu']}% | RAM: {stats['ram']}% | Disk: {stats['disk']}%")
    except Exception as e:
        print(f"❌ Error: {e}")
    time.sleep(2)

h1ER flask import Flask, jsonify, Response
import random
import threading

app = Flask(__name__)

# Simulated device state (not connected to real Bluetooth hardware).
state = {
    "connected": False,
    "ringing": False,
    "battery": 100,
}
lock = threading.Lock()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Key Finder - Dummy Interface</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh; display: flex; justify-content: center;
      align-items: center; padding: 18px; background: #1e1e2e;
      color: white; font-family: Arial, sans-serif;
    }
    .device {
      width: 320px; max-width: 100%; padding: 20px 18px;
      border-radius: 18px; text-align: center; background: #29293b;
      box-shadow: 0 12px 35px #0006;
    }
    h1 { margin: 0 0 16px; font-size: 25px; letter-spacing: 2px; }
    .screen {
      background: #000; color: #00ff88; padding: 9px 5px;
      margin: 6px 0; border-radius: 4px;
      font-family: "Courier New", monospace; font-size: 13px;
      overflow-wrap: anywhere;
    }
    .indicators {
      display: flex; justify-content: space-around; align-items: center;
      margin: 22px 0 16px;
    }
    .led {
      width: 42px; height: 42px; border-radius: 50%;
      background: #333; border: 2px solid white; margin: 0 auto 7px;
    }
    .led.on { background: #ff3b3b; box-shadow: 0 0 18px #ff3b3b; }
    .buzzer { color: #ffcc00; font-size: 17px; min-width: 95px; }
    button {
      width: 90%; border: 0; border-radius: 7px; padding: 13px 8px;
      margin: 6px 0; color: white; font-size: 14px; font-weight: bold;
      cursor: pointer;
    }
    button:active { transform: scale(.98); }
    .find { background: #4caf50; }
    .stop { background: #f44336; }
    .pair { background: #2196f3; }
    #notice { min-height: 18px; color: #ffcc00; font-size: 12px; margin-top: 8px; }
    .note { color: #aaa; font-size: 10px; margin-top: 12px; }
  </style>
</head>
<body>
  <main class="device">
    <h1>KEY FINDER BY HAPPINESS</h1>
    <div class="screen" id="status">Status: DISCONNECTED</div>
    <div class="screen" id="signal">Signal: -- dBm | Dist: -- m</div>
    <div class="screen" id="battery">Battery: 100%</div>

    <div class="indicators">
      <div><div class="led" id="led"></div><div>LED</div></div>
      <div><div class="buzzer" id="buzzer">(silent)</div><div>BUZZER</div></div>
    </div>

    <button class="find" onclick="sendCommand('/api/find')">FIND KEY</button>
    <button class="stop" onclick="sendCommand('/api/stop')">STOP</button>
    <button class="pair" onclick="sendCommand('/api/pair')">PAIR / UNPAIR</button>

    <div id="notice" aria-live="polite"></div>
    <div class="note">Demonstration only — no physical key finder is connected.</div>
  </main>

  <script>
    let ledOn = false;

    async function apiRequest(url) {
      const response = await fetch(url, { method: 'POST' });
      const result = await response.json();
      document.getElementById('notice').textContent = result.message || '';
      await refreshStatus();
    }

    async function sendCommand(url) {
      try {
        await apiRequest(url);
      } catch (error) {
        document.getElementById('notice').textContent =
          'Cannot contact the server. Please refresh the page.';
      }
    }

    async function refreshStatus() {
      const response = await fetch('/api/status');
      const data = await response.json();

      document.getElementById('status').textContent = 'Status: ' + data.message;
      document.getElementById('battery').textContent = 'Battery: ' + data.battery + '%';
      document.getElementById('signal').textContent = data.connected
        ? `Signal: ${data.rssi} dBm | Dist: ${data.distance} m`
        : 'Signal: -- dBm | Dist: -- m';

      if (!data.ringing) {
        ledOn = false;
        document.getElementById('led').classList.remove('on');
        document.getElementById('buzzer').textContent = '(silent)';
      }
    }

    async function animateAlarm() {
      try {
        const response = await fetch('/api/status');
        const data = await response.json();

        document.getElementById('status').textContent = 'Status: ' + data.message;
        document.getElementById('battery').textContent = 'Battery: ' + data.battery + '%';
        document.getElementById('signal').textContent = data.connected
          ? `Signal: ${data.rssi} dBm | Dist: ${data.distance} m`
          : 'Signal: -- dBm | Dist: -- m';

        if (data.ringing) {
          ledOn = !ledOn;
          document.getElementById('led').classList.toggle('on', ledOn);
          document.getElementById('buzzer').textContent = ledOn ? 'BEEP!' : '(...)';
        } else {
          ledOn = false;
          document.getElementById('led').classList.remove('on');
          document.getElementById('buzzer').textContent = '(silent)';
        }
      } catch (error) {
        document.getElementById('notice').textContent = 'Server connection lost.';
      }
    }

    setInterval(animateAlarm, 400);
    refreshStatus();
  </script>
</body>
</html>
"""


def current_status():
    with lock:
        if state["connected"]:
            rssi = random.randint(-90, -40)
            distance = round(10 ** ((-59 - rssi) / 20), 1)
            if state["battery"] > 0 and random.random() < 0.1:
                state["battery"] -= 1
        else:
            rssi = None
            distance = None

        return {
            "connected": state["connected"],
            "ringing": state["ringing"],
            "battery": state["battery"],
            "rssi": rssi,
            "distance": distance,
        }


@app.route("/")
def home():
    return Response(HTML, mimetype="text/html")


@app.get("/api/status")
def status():
    data = current_status()
    data["message"] = (
        "RINGING..." if data["ringing"] else
        "CONNECTED" if data["connected"] else
        "DISCONNECTED"
    )
    return jsonify(data)


@app.post("/api/pair")
def pair():
    with lock:
        state["ringing"] = False
        state["connected"] = not state["connected"]
        connected = state["connected"]

    return jsonify({
        "ok": True,
        "connected": connected,
        "message": "CONNECTED" if connected else "DISCONNECTED"
    })


@app.post("/api/find")
def find_key():
    with lock:
        if not state["connected"]:
            return jsonify({
                "ok": False,
                "message": "NOT PAIRED! Please pair the device first."
            }), 400
        state["ringing"] = True

    return jsonify({"ok": True, "message": "RINGING..."})


@app.post("/api/stop")
def stop_alarm():
    with lock:
        state["ringing"] = False
        connected = state["connected"]

    return jsonify({
        "ok": True,
        "message": "CONNECTED" if connected else "DISCONNECTED"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

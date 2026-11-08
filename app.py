from flask import Flask, jsonify, render_template
import random
import threading

app = Flask(__name__)

# Demo state only: this resets whenever the server restarts.
state = {
    "connected": False,
    "ringing": False,
    "battery": 100,
    "rssi": None,
    "distance": None,
}
lock = threading.Lock()


def get_status():
    """Update simulated signal and battery values, then return a safe copy."""
    with lock:
        if state["connected"]:
            state["rssi"] = random.randint(-90, -40)
            state["distance"] = round(10 ** ((-59 - state["rssi"]) / 20), 1)
            if state["battery"] > 0 and random.random() < 0.1:
                state["battery"] -= 1
        else:
            state["rssi"] = None
            state["distance"] = None

        return {
            "connected": state["connected"],
            "ringing": state["ringing"],
            "battery": state["battery"],
            "rssi": state["rssi"],
            "distance": state["distance"],
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/status")
def status():
    data = get_status()
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
        if not state["connected"]:
            state["rssi"] = None
            state["distance"] = None
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
    app.run(host="0.0.0.0", port=5000, debug=True)

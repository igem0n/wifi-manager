from werkzeug.exceptions import HTTPException
import wifi_manager
from systemd import journal
from flask import Flask, request, jsonify, abort, json, render_template

app = Flask(__name__)
# Bootstrap(app)
wifi = wifi_manager.WifiManager("wlan0", "192.168.42.1")

@app.get("/available")
def get_wifi_networks():
    """Return the cached Wi-Fi networks and signal levels."""
    return jsonify({"networks" : wifi.wifi_networks})

@app.get("/rescan")
def rescan_wifi_networks():
    """Forces scan of Wi-Fi networks and signal levels."""
    return jsonify({"networks" : wifi.rescan_networks()})

@app.get("/status")
def get_wifi_status():
    """Return the cached Wi-Fi active connection status."""
    return jsonify({
        "active" : wifi.active_connections,
        "hotspot" : wifi.hotspot_mode
    })

@app.post("/connect")
def post_connect_to_wifi():
    data = request.get_json()
    ssid = data.get('ssid')
    password = data.get('password')
    #if connect_to_wifi_netowrk(ssid, password):
    if wifi.connect_to_wifi(ssid, password):
        return jsonify({"result" : "ok"})
    else:
        abort(400)

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.get('/')
def ssid_login():
    return render_template('index.html')

if __name__ == "__main__":
    journal.send("application start")
    try:
        wifi.start()
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
        # signal.pause()
    finally:
        wifi.stop()
        journal.send("application stop")
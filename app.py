from werkzeug.exceptions import HTTPException
from  wifi_manager import WifiManager
import configparser, os
from flask import Flask, request, jsonify, abort, json, render_template

app = Flask(__name__)
default_config = {
    "DEFAULT": {
        "interface": "wlan0",
        "gateway": "192.168.10.1",
        "port": "5000"
    }
}

def readConfig():
    config_path = os.getenv("WIFI_MANAGER_CONFING", "/etc/wifi-manager/wifi-manager.conf")
    parser = configparser.ConfigParser()
    parser.read_dict(default_config)
    parser.read(config_path)
    interface = parser["DEFAULT"]["interface"]
    gateway = parser["DEFAULT"]["gateway"]
    port = parser["DEFAULT"]["port"]
    return {"interface" : interface, "gateway" : gateway, "port" : port}


wifi : WifiManager

@app.get("/wifi/available")
def get_wifi_networks():
    """Return the cached Wi-Fi networks and signal levels."""
    return jsonify({"networks" : wifi.wifi_networks})

@app.post("/wifi/rescan")
def rescan_wifi_networks():
    """Forces scan of Wi-Fi networks and signal levels."""
    return jsonify({"networks" : wifi.rescan_networks()})

@app.get("/wifi/status")
def get_wifi_status():
    """Return the cached Wi-Fi active connection status."""
    return jsonify({
        "active" : wifi.active_connections,
        "hotspot" : wifi.hotspot_mode
    })

@app.post("/wifi/connect")
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
    try:
        app_config = readConfig()
        wifi = WifiManager(app_config["interface"], app_config["gateway"])
        wifi.start()
        app.run(host="0.0.0.0", port=app_config["port"], use_reloader=False)
    finally:
        if wifi:
            wifi.stop()
        
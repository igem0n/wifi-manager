from werkzeug.exceptions import HTTPException
from  wifi_manager import WifiManager
from flask import Flask, request, jsonify, abort, json, render_template
from wifi_manager_conf import wifi_manager_config
import atexit

def create_app():
    app = Flask(__name__)
    wifi = WifiManager(wifi_manager_config["interface"], wifi_manager_config["gateway"])

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
    
    def stopWifiManager():
        wifi.stop()

    atexit.register(stopWifiManager)
    wifi.start()

    return app
    
app = create_app()

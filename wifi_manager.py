import time
import cli_tools
from systemd import journal
from threading import Lock, Thread, Event

class WifiManager:
    def __init__(self, interface : str, hotspot_ip : str):
        self._wifi_networks = []
        self._active_connections = []
        self._hotspot_mode = False
        self._interface = interface
        self._hotspot_ip = hotspot_ip
        self._manage_lock = Lock()
        self._stop_event = Event()
        self._worker = Thread(target=self._manage_loop)
        
    def __del__(self):
        self.stop()

    def start(self):
        self._worker.start()

    def stop(self):
        if self._worker.is_alive():
            self._stop_event.set()
            self._worker.join()
            
    def connect_to_wifi(self, ssid : str, password : str):
        with self._manage_lock:
            hotspot_mode = self._hotspot_mode
            if self._hotspot_mode: self.enterNormalMode()
            result = cli_tools.connect_to_wifi_netowrk(ssid, password)
            if hotspot_mode and not result: self.enterHotspotMode()
            return result
        
    def rescan_networks(self):
        with self._manage_lock:
            hotspot_mode = self._hotspot_mode
            if self._hotspot_mode: self.enterNormalMode()
            self._wifi_networks = cli_tools.scan_wifi_networks()
            if hotspot_mode: self.enterHotspotMode()
        return self._wifi_networks

    @property
    def hotspot_mode(self):
        return self._hotspot_mode
    
    @property
    def wifi_networks(self):
        return self._wifi_networks
    
    @property
    def active_connections(self):
        return self._active_connections

    def _enterHotspotMode(self):
        cli_tools.stop_service("NetworkManager")
        cli_tools.set_static_ip(self._interface, self._hotspot_ip)
        cli_tools.start_service("isc-dhcp-server")
        cli_tools.start_service("hostapd")
        self._hotspot_mode = True
    
    def _enterNormalMode(self):
        cli_tools.stop_service("hostapd")
        cli_tools.stop_service("isc-dhcp-server")
        cli_tools.start_service("NetworkManager")
        self._hotspot_mode = False
    
    def _manage_loop_interval(self):
        if self._hotspot_mode: return 60
        else:
            if self._active_connections: return 15
            else: return 5
    
    def _manageHotspot(self):
        if cli_tools.get_connected_host_ap_clients():
            return
        self._enterNormalMode()
    
    def _manageNormal(self):
        self._wifi_networks = cli_tools.scan_wifi_networks()
        self._active_connections = cli_tools.get_active_wifi_connections(self._interface)
        if not self._active_connections:
            journal.send("No connection to wifi, switch to hotspot mode")
            self._enterHotspotMode()

    def _manage_loop(self):
        journal.send("Wifi management loop started")
        self._enterNormalMode()
        self._wifi_networks = cli_tools.scan_wifi_networks()
        self._active_connections = cli_tools.get_active_wifi_connections(self._interface)
        while not self._stop_event.wait(self._manage_loop_interval()):
            with self._manage_lock:
                if self._hotspot_mode: self._manageHotspot()
                else: self._manageNormal()
        journal.send("Wifi management loop finished")
                

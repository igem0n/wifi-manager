import configparser, os

def readConfig():
    default_config = {
        "DEFAULT": {
            "interface": "wlan0",
            "gateway": "192.168.10.1",
            "port": "5000"
        }
    }
    config_path = os.getenv("WIFI_MANAGER_CONFING", "/etc/wifi-manager/wifi-manager.conf")
    parser = configparser.ConfigParser()
    parser.read_dict(default_config)
    parser.read(config_path)
    interface = parser["DEFAULT"]["interface"]
    gateway = parser["DEFAULT"]["gateway"]
    port = parser["DEFAULT"]["port"]
    return { "interface" : interface, "gateway" : gateway, "port" : port }

wifi_manager_config = readConfig()
bind = "0.0.0.0:" + wifi_manager_config["port"]
workers = 1
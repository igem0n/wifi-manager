import subprocess, re
from systemd import journal

mac_address_regex = re.compile(r'(?:[0-9a-fA-F]:?){12}')

def run_command(command):
    """Run a shell command and return the output."""
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return proc.stdout.strip()

def start_service(service_name : str):
    run_command(["systemctl", "start", service_name + ".service"])

def stop_service(service_name : str):
    run_command(["systemctl", "stop", service_name + ".service"])

def set_static_ip(interface : str, ip : str):
    run_command(["ifconfig", interface, ip])

def nmcli_list_command(command : str, keys):
    args = ["nmcli", "-t", "-f", ",".join(keys)] + command
    command_result = run_command(args)
    return [{key: value for key, value in zip(keys, line.split(":"))} for line in command_result.split("\n")]

def scan_wifi_networks():
    keys = ["SSID", "Signal"]
    try:
        return nmcli_list_command(["dev", "wifi", "list", "--rescan", "yes"], keys)
    except Exception:
        return []

def get_active_wifi_connections(interface : str):
    keys = ["NAME", "DEVICE"]
    try:
        active_connections = nmcli_list_command(["con", "show", "--active"], keys)
        return [con["NAME"] for con in active_connections if con["DEVICE"] == interface]
    except Exception:
        return []

def get_connected_host_ap_clients():
    try:
        return mac_address_regex.findall(run_command(["hostapd_cli", "list_sta"]))
    except Exception:
        return []

def connect_to_wifi_netowrk(ssid : str, password : str):
    try:
        run_command(["nmcli", "device", "wifi", "connect", ssid, "password", password])
        return True
    except Exception as e:
        return False
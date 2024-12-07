# Wi-Fi Manager Service 
This Python-based service monitors Wi-Fi networks using `nmcli`, manages Wi-Fi connections, and can switch to hotspot mode if no network is available. It also exposes a simple API for fetching available networks and forcing connections via HTTP requests.
## Features 
 
- Monitor available Wi-Fi networks using `nmcli`.

- Switch to hotspot mode when no network is connected.
 
- Expose a REST API to: 
  - Get available networks (`GET /wifi-networks`).
 
  - Force a connection to a specified network (`POST /connect`).

## Requirements 
 
1. **Python**  (Python 3.x recommended)
 
2. **nmcli**  (part of `NetworkManager` for managing Wi-Fi)
 
3. **systemd**  (for service management)
 
4. **isc-dhcp-server**  (for DHCP in hotspot mode)
 
5. **hostapd**  (for creating a Wi-Fi hotspot)

### Installing Dependencies 

Install necessary dependencies using the following commands:


```bash
# Install Python 3 and pip if not installed
sudo apt update
sudo apt install python3 python3-pip

# Install required Python packages
pip3 install Flask

# Install NetworkManager (nmcli), isc-dhcp-server, and hostapd
sudo apt install network-manager isc-dhcp-server hostapd
```

### Enabling Required Daemons 

Make sure that the following services are enabled and running on your system:
 
1. **NetworkManager** : This service is required for `nmcli` to manage network connections.

```bash
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```
 
2. **isc-dhcp-server** : This service provides DHCP when in hotspot mode.

```bash
sudo systemctl enable isc-dhcp-server
sudo systemctl start isc-dhcp-server
```
 
3. **hostapd** : This service is used to create a Wi-Fi hotspot when switching to hotspot mode.

```bash
sudo systemctl enable hostapd
sudo systemctl start hostapd
```

## Installing the Wi-Fi Manager Service 

### 1. Clone the Repository 

Clone the repository to your desired directory:


```bash
git clone https://github.com/yourusername/wifi-manager.git
cd wifi-manager
```

### 2. Create the Python Script 
Create a new Python script (`wifi_manager.py`) in the directory and paste the Python code provided in the earlier response.
### 3. Set Up the Systemd Service 
Create a `systemd` service unit file to manage the Wi-Fi manager service. 
1. Create a new `wifi-manager.service` file in `/etc/systemd/system/`:

```bash
sudo nano /etc/systemd/system/wifi-manager.service
```
 
2. Paste the following configuration into the file:


```ini
[Unit]
Description=Wi-Fi Manager Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your/script/wifi_manager.py
Restart=always
KillMode=control-group
KillSignal=SIGTERM
TimeoutStopSec=10
User=root
Group=root

[Install]
WantedBy=multi-user.target
```
**Note** : Replace `/path/to/your/script/wifi_manager.py` with the actual path where your Python script is located.
 
3. Reload the `systemd` configuration to recognize the new service:

```bash
sudo systemctl daemon-reload
```
 
4. Enable and start the Wi-Fi manager service:


```bash
sudo systemctl enable wifi-manager
sudo systemctl start wifi-manager
```
4. Configure `hostapd` and `isc-dhcp-server`In case you want to use the system as a hotspot, you need to configure `hostapd` and `isc-dhcp-server`: 
1. **hostapd Configuration** : Configure `hostapd` to create a Wi-Fi access point.Edit the `/etc/hostapd/hostapd.conf` file:

```bash
sudo nano /etc/hostapd/hostapd.conf
```

Example configuration:


```ini
interface=wlan0
driver=nl80211
ssid=MyHotspot
hw_mode=g
channel=6
wpa=2
wpa_passphrase=MyHotspotPassword
```
Update `/etc/default/hostapd` to point to the config file:

```bash
sudo nano /etc/default/hostapd
```

Add or modify this line:


```bash
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```
 
2. **isc-dhcp-server Configuration** : Configure `isc-dhcp-server` to assign IP addresses in hotspot mode.Edit the `/etc/dhcp/dhcpd.conf` file:

```bash
sudo nano /etc/dhcp/dhcpd.conf
```

Example configuration:


```ini
subnet 192.168.42.0 netmask 255.255.255.0 {
    range 192.168.42.10 192.168.42.50;
    option domain-name-servers 8.8.8.8;
    option routers 192.168.42.1;
}
```
Edit the `/etc/default/isc-dhcp-server` to specify the interface:

```bash
sudo nano /etc/default/isc-dhcp-server
```
Set the `INTERFACES` variable:

```bash
INTERFACES="wlan0"
```
 
3. Restart the services:


```bash
sudo systemctl restart hostapd
sudo systemctl restart isc-dhcp-server
```

## Using the Wi-Fi Manager Service 

Once the service is running, you can interact with the Wi-Fi Manager API:

### 1. Get Available Networks 
To get a list of available Wi-Fi networks, send a `GET` request to the `/wifi-networks` endpoint:

```bash
curl http://localhost:5000/wifi-networks
```

### 2. Force Connect to a Network 
To attempt connecting to a specific Wi-Fi network, send a `POST` request with the SSID and password to the `/connect` endpoint:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"ssid":"YourSSID","password":"YourPassword"}' http://localhost:5000/connect
```


---


## Troubleshooting 
 
- **Service not starting** : Check the `systemd` service logs for errors:

```bash
sudo journalctl -u wifi-manager
```
 
- **Wi-Fi connection issues** : Check the `nmcli` output to debug Wi-Fi issues.
 
- **Hotspot not working** : Ensure that `hostapd` and `isc-dhcp-server` are properly configured and running.



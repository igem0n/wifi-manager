# Wi-Fi Manager Service 
This Python-based service monitors Wi-Fi connection status with `nmcli`, and can switch to hotspot mode if no network is available. It also exposes a simple API for fetching available networks and forcing connections via HTTP requests.
## Features 
 
- Monitor available Wi-Fi networks using `nmcli`.

- Automatic switch to hotspot mode when there is no known wifi network and periodic rescan and reconnect attempt if any is available again.

- Simple web page to see the current status and reconnect to another wifi network
 
- Expose a REST API to: 
  - Get available networks (`GET /wifi/available`).
  - Get actual connection status (`GET /wifi/status`)
  - Force networks available networks rescan (`POST /wifi/rescan`).
  - Force a connection to a specified network (`POST /wifi/connect`).

## Requirements 
 
1. **Python**  (Python 3.x recommended)
 
2. **nmcli**  (part of `NetworkManager` for managing Wi-Fi)
 
3. **systemd**  (for service management)
 
4. **isc-dhcp-server**  (for DHCP in hotspot mode)
 
5. **hostapd**  (for creating a Wi-Fi hotspot)

## Installing the Wi-Fi Manager Service 

### 1. Clone the Repository 

Clone the repository to your desired directory:

```bash
git clone git@github.com:igem0n/wifi-manager.git
cd wifi-manager
```

### 2. Installing Dependencies 

Install necessary dependencies using the following commands:


```bash
# Install Python 3 and pip if not installed
sudo apt update
sudo apt install python3 python3-pip libsystemd-dev

# Install NetworkManager (nmcli), isc-dhcp-server, and hostapd
sudo apt install network-manager isc-dhcp-server hostapd

# Install required Python packages
. .venv/bin/activate
pip install -r requirements.txt

```

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
 
### 3. Set up hotspot services 
Configure `hostapd` and `isc-dhcp-server`

1. **hostapd Configuration** : Configure `hostapd` to create a Wi-Fi access point.
Edit the `/etc/hostapd/hostapd.conf` file:

```bash
sudo nano /etc/hostapd/hostapd.conf
```

Example configuration, **interface should be set identical with our wifi service config**:


```ini
interface=wlan0
driver=nl80211
country_code=XX
hw_mode=g
channel=7
ssid=MyAccessPoint
wpa=2
auth_algs=1
wpa_passphrase=12345678
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_pairwise=CCMP
wmm_enabled=1
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
```
Update `/etc/default/hostapd` to point to the config file:

```bash
sudo nano /etc/default/hostapd
```

Add or modify this line:

```ini
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```
 
2. **isc-dhcp-server Configuration** : Configure `isc-dhcp-server` to assign IP addresses in hotspot mode.Edit the `/etc/dhcp/dhcpd.conf` file:

```bash
sudo nano /etc/dhcp/dhcpd.conf
```

Example configuration, **router ip should be set identical with our wifi service config**:

```ini
authoritative;
subnet 192.168.42.0 netmask 255.255.255.0 {
        range 192.168.42.10 192.168.42.50;
        option broadcast-address 192.168.42.255;
        option routers 192.168.42.1;
        default-lease-time 600;
        max-lease-time 7200;
        option domain-name "local";
        option domain-name-servers 8.8.8.8, 8.8.4.4;
}
```
Edit the `/etc/default/isc-dhcp-server` to specify the interface:

```bash
sudo nano /etc/default/isc-dhcp-server
```
Set the `INTERFACES` variable, **it should be set identical with our wifi service config**:

```bash
INTERFACESv4="wlan0"
INTERFACESv6=""
```
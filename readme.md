# Wi-Fi Manager Service 
This background service was designed for home linux-based headless servers connected to the local network over Wi-Fi and it allows to avoid a hassle with resetting Wi-Fi if somewhing was changed. Just connect to the automatically raised hotspot and send new network SSID and password with a simple web interface.
### How it works 
The service monitors Wi-Fi connection status with `nmcli` and if there is no active one, it stops `NetworkManager` service, manually sets static IP for wlan interface using `ifconfig`, starts `isc-dhcp-server` and finally starts `hostapd`.
### What if my WiFi recovers back?
Even being in hotspot mode, service periodically swithes back to the NetworkManager controlled state and rescans networks. If any known Wi-Fi is found, it will reconnect to it. Be aware that periodic recheck is disabled if someone is connected to the hotspot.

## Features 
 
- Monitor available Wi-Fi networks using `nmcli`.

- Automatic switch to hotspot mode when there is no known Wi-FI network and periodic rescan and reconnect attempt if any is available again.

- Simple web page to see the current status and reconnect to another Wi-Fi network
 
- REST API to: 
  - Get available networks (`GET /wifi/available`).
  - Get actual connection status (`GET /wifi/status`)
  - Force rescan (`POST /wifi/rescan`).
  - Connect to the specified network (`POST /wifi/connect`).

## Requirements 
 
1. **Python**  (Python 3.x recommended)
 
2. **nmcli**  (part of `NetworkManager` for managing Wi-Fi)
 
3. **systemd**  (for service management)
 
4. **isc-dhcp-server**  (for DHCP in hotspot mode)
 
5. **hostapd**  (for creating a Wi-Fi hotspot)

Service doesn't provide any automatic configuration of the dependencies. You should set up dhcp and hostapd configuration manually before using it. There are configs examples below.

## Set up guide

### 1. Clone the Repository 

Clone the repository to your desired directory:

```bash
git clone git@github.com:igem0n/wifi-manager.git
cd wifi-manager
```

### 2. Install dependencies 

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
- Create a new `wifi-manager.service` file in `/etc/systemd/system/`:

```bash
sudo nano /etc/systemd/system/wifi-manager.service
```
 
- Paste the following configuration into the file:

```ini
[Unit]
Description=WiFi Monitoring Service
After=network.target

[Service]
ExecStart=/home/orangepi/wifi_manager/.venv/bin/python /home/orangepi/wifi_manager/app.py
Restart=always
KillMode=control-group
KillSignal=SIGTERM
TimeoutStopSec=10
User=root
Group=root
Environment="PATH=/home/orangepi/wifi_manager/.venv/bin:/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```
**Note** : Replace `/home/orangepi/wifi_manager` with the actual path where your cloned this repo.
 
- Reload the `systemd` configuration to recognize the new service:

```bash
sudo systemctl daemon-reload
```
 
### 4. Hostapd service configuration

Configure `hostapd` to create a Wi-Fi access point:
- Edit the `/etc/hostapd/hostapd.conf` file:

```bash
sudo nano /etc/hostapd/hostapd.conf
```

Example configuration, **interface should be set identical with our Wi-Fi manager service config, also set you own SSID and passphrase there**:


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
- Update `/etc/default/hostapd` to point to the config file:

```bash
sudo nano /etc/default/hostapd
```

- Add or modify this line:

```ini
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```
 
### 5. DHCP service configuration 
Configure `isc-dhcp-server` to assign IP addresses in hotspot mode.
- Edit the `/etc/dhcp/dhcpd.conf` file:

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
- Edit the `/etc/default/isc-dhcp-server` to specify the interface:

```bash
sudo nano /etc/default/isc-dhcp-server
```
- Set the `INTERFACES` variable, **it should be set identical with our wifi service config**:

```ini
INTERFACESv4="wlan0"
INTERFACESv6=""
```

### 6. Manually check the set up
Run the following commands to make sure that hotspot runs correctly and NetworkManager is able to reconnect after being restarted.

- List Wi-Fi networks, make sure you see your usual Wi-Fi's there:

```bash
sudo nmcli -t -f SSID,Signal dev wifi list --rescan yes
```

- Check active connection, one of them the should be your Wi-Fi name:

```bash
sudo nmcli -t -f NAME,DEVICE con show --active
```

- Switch to the hotspot mode, you should be able to connect to the hotspot and access all the services running on your server via IP previously set as a router:

```bash
sudo systemctl stop NetworkManager.service
sudo ifconfig wlan0 192.168.42.1
sudo systemctl start isc-dhcp-server.service
sudo systemctl start hostapd.service
```

- List active hotpot connections, you should see MAC-address-like entries for each of the connected device:
```bash
sudo hostapd_cli list_sta
```

- Switch back to the normal Wi-Fi mode, network manager should reconnect to your home Wi-Fi as usual:

```bash
sudo systemctl stop hostapd.service
sudo systemctl stop isc-dhcp-server.service
sudo systemctl start NetworkManager.service
```

### 7. Run and test Wi-Fi manager service
If previous steps worked, try to run our service and test if it's functioning using API and compare results to commands output from previous step.

- Start service:
```bash
sudo systemctl start wifi-manager.service
```

- Check status, it should be running:
```bash
sudo systemctl status wifi-manager.service
```

- Check systemd journal, there shouldn't be any exceptions or errros:
```bash
journalctl -u wifi-manager.service -f
```

- Test endpoints listed above, for the `connect` command you should pass JSON object in the request body with `ssid` and `password` fields:
```json
{
  "ssid": "ssid",
  "password": "password"
}
```

- If everything is working, you can set the serive for automatic start whith the system:

```bash
sudo systemctl enable wifi-manager.service
```

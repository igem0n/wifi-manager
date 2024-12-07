async function fetchNetworks(forceRescan = false) {
    const networkList = document.getElementById('networks');
    const rescanButton = document.getElementById('rescan');
    if(forceRescan) {
        rescanButton.disabled = true;
        networkList.disabled = true;
    }
    const response = await fetch(forceRescan ? '/rescan' : '/available');
    if(!response.ok) {
        rescanButton.disabled = false;
        networkList.disabled = false;
        return;
    }
    const networks = await response.json();
    networkList.innerHTML = '';
    networks.networks.forEach(network => {
        const option = document.createElement('option');
        option.value = network.SSID;
        option.textContent = `${network.SSID} (${network.Signal}%)`;
        networkList.appendChild(option);
    });
    rescanButton.disabled = false;
    networkList.disabled = false;
}

async function fetchStatus() {
    const response = await fetch('/status');
    if(!response.ok) {
        return;
    }
    const status = await response.json();
    const statusElement = document.getElementById('status');
    if(status.hotspot) {
        statusElement.innerText = 'Hotspot mode';
    }
    else if(status.active.length) {
        statusElement.innerText = 'Connected to ' + status.active[0];
    }
    else {
        statusElement.innerText = 'No active connection';
    }
}

async function connectNetwork() {
    const ssid = document.getElementById('ssid').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ssid, password }),
    });

    alert(response.ok ? "ok" : "fail");
}

setInterval(fetchStatus, 5000);
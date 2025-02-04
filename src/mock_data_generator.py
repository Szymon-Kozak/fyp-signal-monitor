import random
import time

def generate_mock_signal_data():
    """
    Generate randomized data similar to what 'wstalist' returns on a PowerBeam device.
    Returns a Python list of dicts, each with fields closely matching real wstalist output.
    """
    mock_station = {
        "mac": "44:D9:E7:DA:71:EB",
        "name": "PowerBeam M5 4",
        "lastip": "192.168.1.99",  # We'll override this at call if we want
        "associd": random.randint(1, 5),
        "aprepeater": random.choice([0, 1]),
        "tx": round(random.uniform(100, 200), 3),
        "rx": round(random.uniform(100, 200), 3),
        "signal": random.randint(-80, -30),
        "rssi": random.randint(30, 70),
        "chainrssi": [random.randint(30, 70), random.randint(30, 70)],
        "rx_chainmask": 3,
        "ccq": random.randint(70, 100),
        "idle": 0,
        "tx_latency": random.randint(1, 5),
        "uptime": random.randint(100, 50000),
        "ack": random.randint(10, 30),
        "distance": random.randint(0, 2000),
        "txpower": random.randint(-10, 0),
        "noisefloor": random.randint(-99, -94),
        "tx_ratedata": [0]*8,
        "airmax": {
            "priority": 0,
            "quality": 0,
            "beam": -1,
            "signal": 0,
            "capacity": 0
        },
        "stats": {
            "rx_data": random.randint(0, 30000),
            "rx_bytes": random.randint(0, 10000000),
            "rx_pps": random.randint(0, 10),
            "tx_data": random.randint(0, 30000),
            "tx_bytes": random.randint(0, 10000000),
            "tx_pps": random.randint(0, 10)
        },
        "rates": [
            "MCS0","MCS1","MCS2","MCS3","MCS4","MCS5","MCS6","MCS7",
            "MCS8","MCS9","MCS10","MCS11","MCS12","MCS13","MCS14","MCS15"
        ],
        "signals": [0]*15 + [random.randint(-80, -30)],
        "remote_age": random.randint(0, 1000),
        "remote_age_max": random.randint(0, 2000),
        "remote": {
            "version": "XW.ar934x.v6.3.14.33424.240826.1757",
            "uptime": random.randint(100, 60000),
            "hostname": "PowerBeam M5 400",
            "platform": "PowerBeam M5 400",
            "signal": random.randint(-80, -30),
            "tx_power": random.randint(-10, 0),
            "rssi": random.randint(30, 70),
            "chainrssi": [random.randint(30, 70), random.randint(30, 70)],
            "tx_latency": random.randint(1, 5),
            "rx_chainmask": 3,
            "noisefloor": -99,
            "distance": random.randint(0, 2000),
            "tx_ratedata": [0]*8,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cpuload": random.randint(0, 10),
            "totalram": 62136,
            "freeram": random.randint(10000, 60000),
            "netrole": "bridge",
            "tx_bytes": random.randint(0, 10000000),
            "rx_bytes": random.randint(0, 10000000),
            "ccq": random.randint(0, 100),
            "ethlist": [
                {
                    "ifname": "eth0",
                    "enabled": True,
                    "plugged": False,
                    "duplex": False,
                    "speed": 0,
                    "snr": [0,0,0,0],
                    "cable_len": -1
                }
            ]
        }
    }

    # Return as a list (wstalist might show multiple stations, but we do one for simplicity)
    return [mock_station]


def fetch_signal_data_simulation(ap_config, result_queue, all_hosts):
    """
    Thread target function (simulation mode).
    Generates random data mimicking 'wstalist' output and puts the result into the queue.

    We'll also override the 'lastip' of the mock station so that each AP sees
    a "station" that claims to be one of the other APs (if so desired).
    """
    host = ap_config.get("host", "SIMULATED_AP")
    # Create mock data
    data = []
    # For simulation, let's generate station entries for each *other* AP in the set
    for other_host in all_hosts:
        if other_host == host:
            continue
        station_list = generate_mock_signal_data()
        # Override the lastip so it 'points' to the other_host
        station_list[0]["lastip"] = other_host
        data.extend(station_list)

    # Put a tuple: (host, data)
    result_queue.put((host, data))

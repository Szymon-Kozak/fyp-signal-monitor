
# Wireless Signal Monitor

## Project Description
A lightweight Python tool (part of a Final Year Project) for collecting and processing wireless signal metrics from AirOS-based Access Points via SSH. It retrieves real-time metrics such as signal, RSSI, noise, and SNR, then formats and displays them for further analysis. The script now supports polling **multiple APs** concurrently and filters for stations named **“PowerBeam M5 4”**, aggregating all relevant signal data in a single output line per interval.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Szymon-Kozak/fyp-signal-monitor.git
   cd fyp-signal-monitor
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional)** Adjust SSH settings in `ssh_connector.py` or wherever you store constants (e.g., IP, username, key path).  
   You can also add or remove AP entries in `ap_config.py` to update which devices are polled.

## Usage

1. **Run the main script**:
   ```bash
   python src/main.py
   ```

   By default, the script connects to each AP listed in `ap_config.py`, executes `wstalist`, and prints the aggregated signal data (or None for APs that time out).

2. **Use Simulation Mode**:
   ```bash
   python src/main.py --simulation
   ```

   This mode generates randomized “mock” data, useful for testing without a live network.

### When running:
- A single line of comma-separated values is printed every interval.
- Only stations named “PowerBeam M5 4” are parsed, and if multiple such stations appear on an AP, all are listed.
- If an AP does not respond within the timeout window, its data is marked as None.

Stop the script anytime with `Ctrl + C`.

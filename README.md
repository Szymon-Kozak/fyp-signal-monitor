
# Wireless Signal Monitor

## Project Description
A lightweight Python tool (part of a Final Year Project) for collecting and processing wireless signal metrics from AirOS-based Access Points via SSH. It retrieves real-time metrics such as signal, RSSI, and noise floor, then formats and displays them for further analysis. The script supports:

- Polling multiple APs concurrently in parallel threads.
- Filtering stations by name (currently “PowerBeam M5 4”).
- Simulation mode, generating mock data without a live network.
- Logging each poll’s result (directional RSS and noise for each AP) to a CSV file.
- Configurable duration so it can stop automatically after N seconds.

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
   *(On Windows, use `.\.venv\Scripts\activate` instead.)*

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional)** Adjust SSH settings in `ssh_connector.py` or wherever you store constants (e.g., IP, username, key path).  
   You can also add or remove AP entries in `ap_config.py` to update which devices are polled (e.g., multiple APs).

## Usage

1. **Basic Run (Real Mode)**  
   By default, the script connects to every AP in `ap_config.py`, executes `wstalist`, and prints aggregated signal data (or None if APs time out):
   ```bash
   python src/main.py
   ```

2. **Simulation Mode**  
   Use `--simulation` to generate random “mock” data without requiring live APs:
   ```bash
   python src/main.py --simulation
   ```

3. **Limiting Number of APs**  
   Use `--num-aps N` to poll only the first N APs from `ap_list`:
   ```bash
   python src/main.py --num-aps 2
   ```

4. **Specifying Script Duration**  
   Use `--duration <seconds>` to stop automatically after `<seconds>`:
   ```bash
   python src/main.py --duration 60
   ```

5. **Combining Arguments**  
   Combine multiple arguments. For example:
   ```bash
   python src/main.py --simulation --num-aps 2 --duration 30
   ```
   This runs in simulation mode, polling only the first 2 APs for 30 seconds.

## CSV Logging

1. **Dynamic Filename**  
   Each run appends data to (or creates) a CSV file named:
   ```
   data_pull_<simulation_or_real>_<num_aps>_<duration>_<polling_rate>.csv
   ```
   Example: `data_pull_simulation_2_60_0.5.csv`

2. **Header Format**  
   If the CSV does not already exist, a header is created:
   ```
   time, ap2_ap1_rss, ap3_ap1_rss, ..., ap1_noise, ap1_ap2_rss, ap3_ap2_rss, ..., ap2_noise, ...
   ```
   For N APs, there are `N(N-1)` directional RSS columns, `N` noise columns, and a time column.

3. **Appending Data**  
   Each poll writes a new row with time, RSS values, and noise floors.  
   Example row for 2 APs (AP1 at .21 and AP2 at .22):
   ```
   0.501, RSS(AP2->AP1)=-48, noise(AP1)=-95, RSS(AP1->AP2)=-50, noise(AP2)=-99
   ```

## Notes & Tips

- **Persistent SSH**: Opens and reuses SSH sessions, reducing overhead.  
- **Adjust Poll Interval**: Default `POLL_INTERVAL` is 0.5s. Change it in `main.py` as needed.  
- **Timeouts**: If an AP times out, its data is marked as `None`. Adjust `COMMAND_TIMEOUT` if needed.  
- **Stopping**: Stop the script anytime with `Ctrl + C`. SSH sessions will close cleanly.  
- **Data Analysis**: Open the CSV in Excel or load it into Python (e.g., with Pandas) for further analysis.

## Example Commands

1. **Poll All APs, No Time Limit**  
   ```bash
   python src/main.py
   ```

2. **Poll 3 APs for 120 seconds**  
   ```bash
   python src/main.py --num-aps 3 --duration 120
   ```

3. **Simulation Mode, 2 APs, 30 seconds**  
   ```bash
   python src/main.py --simulation --num-aps 2 --duration 30
   ```

Each run produces a CSV file (e.g., `data_pull_simulation_2_30_0.5.csv`) and prints data to the console every half-second. Stop the script anytime with `Ctrl + C`.

# Wireless Signal Monitor

## Project Description
A lightweight Python tool (part of a Final Year Project) for collecting and processing wireless signal metrics from AirOS-based Access Points via SSH. It retrieves real-time metrics such as signal, RSSI, noise, and SNR, then formats and displays them for further analysis.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/<NEW_REPO_NAME>.git
   cd <NEW_REPO_NAME>
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

## Usage
1. **Run the main script**:
   ```bash
   python src/main.py
   ```

The script will:
- Establish an SSH connection to your specified AP.
- Execute `wstalist` (or a similar command) to pull signal metrics.
- Parse and display signal, RSSI, noise, and SNR data in real time.

Stop the script anytime with `Ctrl + C`.

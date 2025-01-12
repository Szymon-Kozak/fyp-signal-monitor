import paramiko
import time
import json
import sys
import os


# SSH connection details
HOST = '192.168.1.21'
USERNAME = 'ubnt'
SSH_KEY_PATH = os.path.expanduser('~/.ssh/id_rsa')

# Command to retrieve signal data
COMMAND = 'wstalist'  # Adjust as needed

# Polling interval in seconds
POLL_INTERVAL = 1  # Adjust as needed

def connect_to_host(host, username, key_path):
    """
    Establish an SSH connection to the specified host and return the client object.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        private_key = paramiko.RSAKey.from_private_key_file(key_path)
        client.connect(
            hostname=host,
            username=username,
            pkey=private_key,
            look_for_keys=False,
            allow_agent=False,
            disabled_algorithms={
                'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']
            }
        )
        return client
    except Exception as e:
        print(f"Error connecting to host {host}: {e}", file=sys.stderr)
        return None

def execute_command(client, command):
    """
    Execute a command on the SSH client and return the output as JSON.
    """
    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if error:
            print(f"Command error: {error}", file=sys.stderr)
            return None

        return json.loads(output)
    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        return None

def parse_signal_data(signal_data):
    """
    Parse and format the raw signal data into a readable tuple format.
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    formatted_data = []
    for entry in signal_data:
        signal = entry.get('signal')
        rssi = entry.get('rssi')
        noise = entry.get('noisefloor')
        snr = signal - noise if signal is not None and noise is not None else None
        formatted_data.append({
            'timestamp': timestamp,
            'signal': signal,
            'rssi': rssi,
            'noise': noise,
            'snr': snr
        })
    return formatted_data

def print_signal_data(parsed_data):
    """
    Print the parsed signal data in a readable format.
    """
    for entry in parsed_data:
        print(
            f"Timestamp: {entry['timestamp']}, "
            f"Signal: {entry['signal']} dBm, "
            f"RSSI: {entry['rssi']}, "
            f"Noise: {entry['noise']} dBm, "
            f"SNR: {entry['snr']} dB"
        )
    print("-" * 40)

def main():
    client = connect_to_host(HOST, USERNAME, SSH_KEY_PATH)
    if not client:
        sys.exit("Failed to establish SSH connection. Exiting.")

    try:
        while True:
            signal_data = execute_command(client, COMMAND)
            if signal_data:
                parsed_data = parse_signal_data(signal_data)
                print_signal_data(parsed_data)
            else:
                print("Failed to retrieve signal data.", file=sys.stderr)

            time.sleep(POLL_INTERVAL)
    finally:
        client.close()


if __name__ == '__main__':
    main()
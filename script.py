import paramiko
import time
import json
import sys
import os
import threading
import queue

# SSH connection details
HOST = '192.168.1.22'
USERNAME = 'ubnt'
SSH_KEY_PATH = os.path.expanduser('~/.ssh/id_rsa')

# Command to retrieve signal data
COMMAND = 'wstalist'

# Polling interval in seconds
POLL_INTERVAL = 1

# Timeout in seconds for each SSH command to return
COMMAND_TIMEOUT = 0.8

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

def fetch_signal_data(client, result_queue):
    """
    Thread target function:
    Executes the wstalist (or similar) command and puts the result into a queue.
    """
    data = execute_command(client, COMMAND)
    result_queue.put(data)

def parse_signal_data(signal_data, offset_seconds):
    """
    Parse and format the raw signal data into a readable tuple format.
    """
    formatted_data = []
    if not signal_data:
        # If None or empty, return a single entry with NULL placeholders
        return [{
            'time_since_start': offset_seconds,
            'signal': None,
            'rssi': None,
            'noise': None,
            'snr': None
        }]

    for entry in signal_data:
        signal = entry.get('signal')
        rssi = entry.get('rssi')
        noise = entry.get('noisefloor')
        snr = signal - noise if signal is not None and noise is not None else None
        formatted_data.append({
            'time_since_start': offset_seconds,
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
        t_str = f"{entry['time_since_start']:.2f}s"
        print(
            f"[{t_str}] "
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

    start_time = time.time()

    try:
        while True:
            # Calculate how many seconds since script started
            offset_seconds = time.time() - start_time

            # Start a thread to fetch data
            result_queue = queue.Queue()
            thread = threading.Thread(target=fetch_signal_data, args=(client, result_queue), daemon=True)
            thread.start()

            # Wait for up to COMMAND_TIMEOUT seconds
            thread.join(COMMAND_TIMEOUT)

            if thread.is_alive():
                # The data wasn't returned in time => fill with NULL
                signal_data = None
            else:
                # If thread is finished then retrieve the data from the queue
                signal_data = result_queue.get()

            # Now parse and print
            parsed_data = parse_signal_data(signal_data, offset_seconds)
            print_signal_data(parsed_data)

            # Sleep to maintain exact intervals from the start of the loop
            loop_end = time.time()
            elapsed = loop_end - (start_time + offset_seconds)
            time_to_sleep = POLL_INTERVAL - elapsed
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
    finally:
        client.close()


if __name__ == '__main__':
    main()
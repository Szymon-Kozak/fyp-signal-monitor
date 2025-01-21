import paramiko
import sys
import os
import json

COMMAND = 'wstalist'

def connect_to_host(host, username, key_path):
    """
    Establish an SSH connection to the specified host and return the client object.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        private_key = paramiko.RSAKey.from_private_key_file(
            os.path.expanduser(key_path)
        )
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

def fetch_signal_data(ap_config, result_queue):
    """
    Thread target function:
    1) Connects to a single AP using SSH.
    2) Executes wstalist.
    3) Puts the retrieved data into result_queue along with the AP's host.
    """
    host = ap_config.get("host")
    username = ap_config.get("username")
    key_path = ap_config.get("ssh_key_path")

    client = connect_to_host(host, username, key_path)
    data = None
    if client:
        data = execute_command(client, COMMAND)
        client.close()

    # Put a tuple: (host, data)
    result_queue.put((host, data))

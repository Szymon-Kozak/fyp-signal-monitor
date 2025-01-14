import paramiko
import sys
import os
import json

HOST = '192.168.1.22'
USERNAME = 'ubnt'
SSH_KEY_PATH = os.path.expanduser('~/.ssh/id_rsa')
COMMAND = 'wstalist'

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
    pass

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
    pass

def fetch_signal_data(client, result_queue):
    """
    Thread target function:
    Executes the wstalist (or similar) command and puts the result into a queue.
    """
    data = execute_command(client, COMMAND)
    result_queue.put(data)
    pass
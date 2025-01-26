import argparse
import queue
import threading
import time
import sys
import csv

from ap_config import ap_list
from ssh_connector import connect_to_host, execute_command
from mock_data_generator import fetch_signal_data_simulation
from data_parser import parse_signal_data
from signal_printer import print_signal_data

POLL_INTERVAL = 0.5
COMMAND_TIMEOUT = 0.45

def parse_arguments():
    parser = argparse.ArgumentParser(description="Wireless Signal Monitor (Multi-AP)")
    parser.add_argument(
        "--simulation", "-s",
        action="store_true",
        help="Enable simulation mode (no SSH, generate random data)"
    )
    parser.add_argument(
        "--num-aps", "-n",
        type=int,
        default=None,
        help="Number of APs to poll (subset of ap_config). If omitted, uses all."
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=None,
        help="Stop the script after N seconds have elapsed."
    )
    return parser.parse_args()

def poll_ssh_connection(host, client, result_queue):
    """
    Thread target function for real mode with a persistent SSH session.
    We just run 'execute_command(client, "wstalist")' and put results into the queue.
    """
    data = None
    if client:
        data = execute_command(client, "wstalist")
    result_queue.put((host, data))

def build_csv_header(ap_hosts):
    """
    Returns a list of column names for the CSV:
      [time, ap2_ap1_rss, ap3_ap1_rss, ap1_noise, ap1_ap2_rss, ...]
    matching the order of the final data row.
    """
    header = ["time"]  # always have 'time' first

    # We'll label APs as AP1, AP2, ...
    label_map = {ap_hosts[i]: f"AP{i+1}" for i in range(len(ap_hosts))}

    # For each "this_ap", we collect columns for:
    #   RSS(other_ap->this_ap) for all other_ap, then noise(this_ap)
    for this_ap in ap_hosts:
        for other_ap in ap_hosts:
            if other_ap == this_ap:
                continue
            # column name like "ap2_ap1_rss"
            header.append(f"{label_map[other_ap].lower()}_{label_map[this_ap].lower()}_rss")
        # column name like "ap1_noise"
        header.append(f"{label_map[this_ap].lower()}_noise")

    return header



def main():
    args = parse_arguments()
    simulation_mode = args.simulation
    num_aps = args.num_aps

    # Slice the AP list if --num-aps is provided
    used_ap_list = ap_list
    if num_aps is not None and num_aps < len(ap_list):
        used_ap_list = ap_list[:num_aps]

    if not used_ap_list:
        print("No APs to poll. Exiting.")
        sys.exit(1)

    # Collect just the hosts for referencing
    used_hosts = [ap["host"] for ap in used_ap_list]
    known_hosts_set = set(used_hosts)

    ssh_clients_map = {}

    # If not simulation, connect once to each AP
    if not simulation_mode:
        for ap in used_ap_list:
            host = ap["host"]
            username = ap["username"]
            key_path = ap["ssh_key_path"]
            client = connect_to_host(host, username, key_path)
            ssh_clients_map[host] = client  # could be None if connect failed

    start_time = time.time()

    try:
        while True:
            loop_start = time.time()
            offset_seconds = loop_start - start_time

            result_queue = queue.Queue()
            threads = []

            for ap in used_ap_list:
                host = ap["host"]
                if simulation_mode:
                    # Simulation: generate mock data with stations
                    t = threading.Thread(
                        target=fetch_signal_data_simulation,
                        args=(ap, result_queue, used_hosts),
                        daemon=True
                    )
                else:
                    client = ssh_clients_map[host]
                    t = threading.Thread(
                        target=poll_ssh_connection,
                        args=(host, client, result_queue),
                        daemon=True
                    )

                threads.append(t)
                t.start()

            # Wait up to COMMAND_TIMEOUT for each thread
            for t in threads:
                t.join(COMMAND_TIMEOUT)

            # Collect whatever data we got
            all_host_data = []
            while not result_queue.empty():
                host, data = result_queue.get()
                all_host_data.append((host, data))

            # Fill in missing hosts with None
            responded_hosts = {hd[0] for hd in all_host_data}
            missing_hosts = set(used_hosts) - responded_hosts
            for mh in missing_hosts:
                all_host_data.append((mh, None))

            # Parse results
            parsed_output = parse_signal_data(
                all_host_data,
                offset_seconds,
                known_hosts=known_hosts_set
            )
            print_signal_data(parsed_output)

            # Sleep for the remainder of the interval
            loop_end = time.time()
            elapsed = loop_end - loop_start
            time_to_sleep = POLL_INTERVAL - elapsed
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

    except KeyboardInterrupt:
        print("\nExiting on user interrupt.")

    finally:
        # Close all persistent SSH sessions
        if not simulation_mode:
            for host, client in ssh_clients_map.items():
                if client is not None:
                    client.close()

    sys.exit(0)

if __name__ == '__main__':
    main()
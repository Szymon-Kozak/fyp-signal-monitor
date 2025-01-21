import argparse
import queue
import threading
import time
import sys

from ap_config import ap_list
from ssh_connector import fetch_signal_data
from mock_data_generator import fetch_signal_data_simulation
from data_parser import parse_signal_data
from signal_printer import print_signal_data

POLL_INTERVAL = 1
COMMAND_TIMEOUT = 0.8

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
    return parser.parse_args()

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

    start_time = time.time()

    try:
        while True:
            loop_start = time.time()
            offset_seconds = loop_start - start_time

            # We'll poll all APs in parallel
            result_queue = queue.Queue()
            threads = []

            for ap in used_ap_list:
                if simulation_mode:
                    # Pass the entire used_hosts so each AP can "see" the others
                    t = threading.Thread(
                        target=fetch_signal_data_simulation,
                        args=(ap, result_queue, used_hosts),
                        daemon=True
                    )
                else:
                    t = threading.Thread(
                        target=fetch_signal_data,
                        args=(ap, result_queue),
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

            # Now parse results
            parsed_output = parse_signal_data(
                all_host_data,
                offset_seconds,
                known_hosts=known_hosts_set
            )

            # Print in one line
            print_signal_data(parsed_output)

            # Sleep for the remainder of the interval
            loop_end = time.time()
            elapsed = loop_end - loop_start
            time_to_sleep = POLL_INTERVAL - elapsed
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

    except KeyboardInterrupt:
        print("\nExiting on user interrupt.")
        sys.exit(0)

if __name__ == '__main__':
    main()
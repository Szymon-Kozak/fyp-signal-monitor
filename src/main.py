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
        "--simulation",
        "-s",
        action="store_true",
        help="Enable simulation mode (no SSH connection, generate random data)"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    simulation_mode = args.simulation

    start_time = time.time()

    try:
        while True:
            offset_seconds = time.time() - start_time

            # We'll poll all APs in parallel
            result_queue = queue.Queue()
            threads = []

            for ap in ap_list:
                if simulation_mode:
                    t = threading.Thread(
                        target=fetch_signal_data_simulation,
                        args=(ap, result_queue),
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
                # If the thread is still alive after join, it won't put anything in queue
                # so that AP will effectively be data=None

            # Collect all data from the queue
            all_host_data = []
            while not result_queue.empty():
                host, data = result_queue.get()
                # host is e.g. "192.168.1.21", data is list-of-dicts or None
                all_host_data.append((host, data))

            # If any AP never responded, we won't have it in all_host_data; let's fill it
            known_hosts = {ap["host"] for ap in ap_list}
            responded_hosts = {hd[0] for hd in all_host_data}
            missing_hosts = known_hosts - responded_hosts
            # For those, push (host, None)
            for mh in missing_hosts:
                all_host_data.append((mh, None))

            # Now parse ALL AP results
            parsed_output = parse_signal_data(all_host_data, offset_seconds)

            # Print in a single line
            print_signal_data(parsed_output)

            # Sleep for the remainder of the interval
            loop_end = time.time()
            elapsed = loop_end - (start_time + offset_seconds)
            time_to_sleep = POLL_INTERVAL - elapsed
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

    except KeyboardInterrupt:
        print("\nExiting on user interrupt.")
        sys.exit(0)

if __name__ == '__main__':
    main()

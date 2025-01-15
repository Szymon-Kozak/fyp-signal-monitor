import argparse
import queue
import threading
import time
import sys
from ssh_connector import connect_to_host, fetch_signal_data
from data_parser import parse_signal_data
from signal_printer import print_signal_data
from mock_data_generator import generate_mock_signal_data

POLL_INTERVAL = 1
COMMAND_TIMEOUT = 0.8

def parse_arguments():
    parser = argparse.ArgumentParser(description="Wireless Signal Monitor")
    parser.add_argument(
        "--simulation",
        "-s",
        action="store_true",
        help="Enable simulation mode (no SSH connection, generate random data for testing purposes)",
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    simulation_mode = args.simulation

    if not simulation_mode:
        # Normal operation: connect via SSH
        client = connect_to_host(...)
        if not client:
            sys.exit("Failed to establish SSH connection. Exiting.")
    else:
        # In simulation mode there is no SSH client needed
        client = None

    start_time = time.time()

    try:
        while True:
            # Calculate how many seconds since script started
            offset_seconds = time.time() - start_time

            # Start a thread to fetch data
            result_queue = queue.Queue()

            if simulation_mode:
                # Thread to fetch mock data
                thread = threading.Thread(
                    target=fetch_signal_data_simulation,
                    args=(result_queue,),
                    daemon=True
                )
            else:
                # Thread to fetch real data
                thread = threading.Thread(
                    target=fetch_signal_data,
                    args=(client, result_queue),
                    daemon=True
                )

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
        if client and not simulation_mode:
            client.close()


if __name__ == '__main__':
    main()
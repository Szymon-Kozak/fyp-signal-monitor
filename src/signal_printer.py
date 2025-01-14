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
    pass
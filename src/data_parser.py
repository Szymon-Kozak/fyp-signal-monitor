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
    pass
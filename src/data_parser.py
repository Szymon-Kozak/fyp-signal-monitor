def parse_signal_data(all_host_data, offset_seconds):
    """
    :param all_host_data: list of (host, data) tuples, where data is either None or
                          a list of station dicts from wstalist.
    :param offset_seconds: float, time offset since script start.
    :return: dict: {
        "time_since_start": offset_seconds,
        "results": {
           host1: [ (signal, noise), (signal, noise), ... ] or None,
           host2: [ (signal, noise), ... ] or None,
           ...
        }
    }

    NOTE: We parse ALL stations with 'name' == "PowerBeam M5 4" for each AP.
          If data is missing or no station matched, the value is None.
    """

    results_dict = {}
    for (host, station_list) in all_host_data:
        if station_list is None:
            # Timed out or error => fill with None
            results_dict[host] = None
            continue

        # Filter for "PowerBeam M5 4" stations
        powerbeam_entries = [s for s in station_list if s.get('name') == "PowerBeam M5 4"]
        if not powerbeam_entries:
            # No matching station
            results_dict[host] = None
            continue

        # Parse every matching station
        parsed_values = []
        for entry in powerbeam_entries:
            signal = entry.get('signal')
            noise = entry.get('noisefloor')
            parsed_values.append((signal, noise))

        results_dict[host] = parsed_values

    return {
        "time_since_start": offset_seconds,
        "results": results_dict
    }

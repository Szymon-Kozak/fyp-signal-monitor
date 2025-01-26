def parse_signal_data(all_host_data, offset_seconds, known_hosts):
    """
    Parse the raw station data from multiple APs and structure it so we know
    the RSS from APx -> APy plus the noise for each AP.
    """
    # Initialize a dict for each host
    results_dict = {}
    for (host, _) in all_host_data:
        results_dict[host] = {}  # will become None if we can't parse

    for (host, station_list) in all_host_data:
        # print(f"Parsing data for host: {host}, station_list: {station_list}")  # Debugging statement
        # If we had a timeout or error, station_list is None
        if station_list is None:
            results_dict[host] = None
            continue

        ap_noise = None

        # Check each station
        for station in station_list:
            # Must match the specific name to be considered
            if station.get('name') == "PowerBeam M5 4":
                if ap_noise is None:
                    ap_noise = station.get('noisefloor')

                remote_ip = station.get('lastip')
                if remote_ip in known_hosts:
                    # We store the signal from this AP's perspective
                    results_dict[host][remote_ip] = station.get('signal')

        # Record noise for this AP if we didn't mark it None
        if results_dict[host] is not None:
            results_dict[host]["noise"] = ap_noise

    return {
        "time_since_start": offset_seconds,
        "results": results_dict
    }
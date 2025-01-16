def print_signal_data(parsed_output):
    """
    Prints data in a single line:
      time_since_start, host1_signal1, host1_noise1, host1_signal2, host1_noise2, ..., hostN_signalX, hostN_noiseX
    If no data from a host, print None/None.
    """

    time_since_start = parsed_output["time_since_start"]
    results_dict = parsed_output["results"]  # { host: [ (signal, noise), ... ] or None }

    line_items = [f"{time_since_start:.2f}"]  # start with time

    sorted_hosts = sorted(results_dict.keys())

    for host in sorted_hosts:
        host_data = results_dict[host]
        if host_data is None:
            # means either timed out or no "PowerBeam M5 4" entry
            line_items.append("None")
            line_items.append("None")
        else:
            for (sig, nos) in host_data:
                line_items.append(str(sig if sig is not None else "None"))
                line_items.append(str(nos if nos is not None else "None"))

    print(",".join(line_items))

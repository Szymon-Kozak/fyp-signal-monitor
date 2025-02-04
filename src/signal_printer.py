def print_signal_data(parsed_output):
    """
    Prints a single line with labels like:
      Timestamp,
      RSS(AP2->AP1)=<val>, RSS(AP3->AP1)=<val>, noise(AP1)=<val>,
      RSS(AP1->AP2)=<val>, RSS(AP3->AP2)=<val>, noise(AP2)=<val>,
      RSS(AP1->AP3)=<val>, RSS(AP2->AP3)=<val>, noise(AP3)=<val>
      ...
    for however many APs are being monitored.
    """
    time_since_start = parsed_output["time_since_start"]
    results_dict = parsed_output["results"]

    # Sort the APs by IP/host for consistent ordering
    ap_hosts = sorted(results_dict.keys())

    # Create a map host -> label, e.g. "192.168.1.21" -> "AP1", etc.
    label_map = {ap_hosts[i]: f"AP{i + 1}" for i in range(len(ap_hosts))}

    # Begin the output line with time
    line_items = [f"{time_since_start:.1f}"]

    # For each "this_ap", we collect: RSS(other_ap->this_ap) for all other_ap, then noise(this_ap)
    # So it looks like:
    #   RSS(AP2->AP1)=..., RSS(AP3->AP1)=..., noise(AP1)=...,
    #   RSS(AP1->AP2)=..., RSS(AP3->AP2)=..., noise(AP2)=...,
    #   ...
    for this_ap in ap_hosts:
        if results_dict[this_ap] is None:
            # Means we had no data (timeout or error) => place None for each link + noise
            for other_ap in ap_hosts:
                if other_ap != this_ap:
                    label = f"RSS({label_map[other_ap]}->{label_map[this_ap]})"
                    line_items.append(f"{label}=None")
            noise_label = f"noise({label_map[this_ap]})"
            line_items.append(f"{noise_label}=None")
            continue

        # For each other_ap
        for other_ap in ap_hosts:
            if other_ap == this_ap:
                continue
            # If the other_ap result is also None, we can't glean a signal
            if results_dict[other_ap] is None:
                signal_val = "None"
            else:
                # e.g. results_dict[other_ap].get(this_ap) => RSS from other_ap->this_ap
                link_signal = results_dict[other_ap].get(this_ap)
                signal_val = link_signal if link_signal is not None else "None"

            label = f"RSS({label_map[other_ap]}->{label_map[this_ap]})"
            line_items.append(f"{label}={signal_val}")

        # Finally noise for this AP
        noise_val = results_dict[this_ap].get("noise")
        noise_label = f"noise({label_map[this_ap]})"
        noise_str = noise_val if noise_val is not None else "None"
        line_items.append(f"{noise_label}={noise_str}")

    # Join all labeled items in one line
    print(", ".join(line_items))

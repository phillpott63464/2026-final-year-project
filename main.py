def main():
    json_paths = ["/data/control.json", "/data/unlabelled.json"]
    data = load_data(json_paths)
    data = scale_data(data)
    plot_data(data)


def load_data(
    json_paths: list # List of paths to json files
) -> dict:
    data_list = []
    for json_path in json_paths:
        data_list.append(load_json(json_path))

    return combine_data(data_list)

def load_json(json_path: str) -> dict:
    # Load json file and return as dict
    import json
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Find column indices
    columns = data['columns']
    peak_num_idx = columns.index('#')
    height_idx = columns.index('Height')
    volume_idx = columns.index('Volume')
    
    # Build output dict
    result = {}
    for row in data['data']:
        peak_num = row[peak_num_idx]
        height = row[height_idx]
        volume = row[volume_idx]
        result[peak_num] = [height, volume]
    
    return result

def combine_data(
    data_list: list # List of dicts
) -> dict:

    data_a, data_b = data_list
    combined_data = {}

    # Output data dict structure:
    # {peak_id: [A_height, A_volume, B_height, B_volume], ...}
    for peak_id in set(data_a.keys()).union(set(data_b.keys())):
        a_height, a_volume = data_a.get(peak_id, (None, None))
        b_height, b_volume = data_b.get(peak_id, (None, None))
        if "None" in [a_height, a_volume, b_height, b_volume]:
            continue
        combined_data[peak_id] = [float(a_height), float(a_volume), float(b_height), float(b_volume)]

    return combined_data


def scale_data(
    data: dict, # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
) -> dict:
    import numpy as np
    scaled_B_heights = []
    scaled_B_volumes = []
    for peak_id, values in data.items():
        temp = values[0] / values[2] # A_height / B_height
        temp2 = values[1] / values[3] # A_volume / B_volume
        scaled_B_heights.append(temp) # Scale B_height
        scaled_B_volumes.append(temp2) # Scale B_volume

    # Median of scaled B
    median_B_height = np.median(scaled_B_heights)
    median_B_volume = np.median(scaled_B_volumes)

    # Scale B to median
    for peak_id, values in data.items():
        if None in values:
            continue
        data[peak_id][2] = values[2] * median_B_height # Scale B_height to median
        data[peak_id][3] = values[3] * median_B_volume # Scale B_volume to median
    
    return data

def plot_data(
    data: dict # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
):
    import matplotlib.pyplot as plt
    # Divide A height by B height and plot the ratios on a bar chart
    ratios = [values[0] / values[2] for values in data.values()]
    ratios = sorted(ratios) # Sort ratios for better visualization
    plt.bar(range(len(ratios)), ratios)
    plt.xlabel('Peak ID')
    plt.ylabel('A_height / B_height')
    plt.title('Ratio of A height to B height')
    plt.savefig('/data/height_ratios.png')

    # Divide A volume by B volume and plot the ratios on a bar chart
    plt.figure() # Create new figure for second plot
    ratios = [values[1] / values[3] for values in data.values()]
    ratios = sorted(ratios) # Sort ratios for better visualization
    plt.bar(range(len(ratios)), ratios)
    plt.xlabel('Peak ID')
    plt.ylabel('A_volume / B_volume')
    plt.title('Ratio of A volume to B volume')
    plt.savefig('/data/volume_ratios.png')

    pass


if __name__ == "__main__":
    main()

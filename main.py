def main():
    json_paths = ["/data/control.json", "/data/unlabelled.json"]

    data = load_data(json_paths)
    scaled_data = scale_data(data)

    plot_data(scaled_data)

    save_data(scaled_data, "/data/scaled_data.json")

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
        temp = values[2] / values[0] # B_height / A_height
        temp2 = values[3] / values[1] # B_volume / A_volume
        scaled_B_heights.append(temp) # Scale B_height
        scaled_B_volumes.append(temp2) # Scale B_volume

    # Median of scaled B
    median_B_height = np.median(scaled_B_heights)
    median_B_volume = np.median(scaled_B_volumes)

    # Scale B to median
    for peak_id, values in data.items():
        data[peak_id][2] = values[2] / median_B_height  # Scale B_height to match A
        data[peak_id][3] = values[3] / median_B_volume  # Scale B_volume to match A
        
    return data

def plot_data(
    data: dict # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
):
    import numpy as np
    import matplotlib.pyplot as plt
    # Set threshold for coloring at 90% of the peaks (temporarily)
    threshold = np.percentile([values[2] / values[0] for values in data.values()], 10)

    # Height ratios
    height_ratios = [values[2] / values[0] for values in data.values()]  # B / A
    colors_height = ['red' if ratio < threshold else 'green' for ratio in height_ratios]
    plt.bar(range(len(height_ratios)), height_ratios, color=colors_height)
    plt.xlabel('Peak ID')
    plt.ylabel('B_height / A_height')
    plt.title('B Height relative to A (median normalized)')
    plt.savefig('/data/height_ratios.png')
    plt.close()

    threshold = np.percentile([values[3] / values[1] for values in data.values()], 10)
    # Volume ratios
    volume_ratios = [values[3] / values[1] for values in data.values()]  # B / A
    colors_volume = ['red' if ratio < threshold else 'green' for ratio in volume_ratios]
    plt.figure()
    plt.bar(range(len(volume_ratios)), volume_ratios, color=colors_volume)
    plt.xlabel('Peak ID')
    plt.ylabel('B_volume / A_volume')
    plt.title('B Volume relative to A (median normalized)')
    plt.savefig('/data/volume_ratios.png')
    plt.close()

def save_data(
    data: dict, # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
    output_path: str
):
    import json
    with open(output_path, 'w') as f:
        # Make readabkle with indent
        json.dump(data, f, indent=1)


if __name__ == "__main__":
    main()

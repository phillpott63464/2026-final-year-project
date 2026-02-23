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

    # Extracted helper to avoid repetition
    def _plot_ratio(data, num_idx, denom_idx, output_path, title, ylabel, cap_value=None):
        # Compute ratios
        ratios = [values[num_idx] / values[denom_idx] for values in data.values()]

        print(np.median(ratios))

        # Determine threshold as 8th lowest ratio (number of phenylalanine peaks)
        threshold = sorted(ratios)[7] 

        if cap_value is not None:
            for i in range(len(ratios)):
                if ratios[i] > cap_value:
                    ratios[i] = cap_value

        colors = ['red' if r < threshold else 'yellow' if r < 0.8 else 'green' for r in ratios]

        save_color_csv(ratios, colors, f'{output_path}_colors.csv')

        plt.figure(figsize=(10, 6))
        plt.bar(range(len(ratios)), ratios, color=colors)
        plt.xlabel('Peak ID')
        plt.ylabel(ylabel)
        plt.title(title)

        red_count = colors.count('red')
        yellow_count = colors.count('yellow')
        green_count = colors.count('green')
        plt.text(0.5, 0.97, f'Red: {red_count}, Yellow: {yellow_count}, Green: {green_count}', ha='center', va='center', transform=plt.gca().transAxes)
        plt.tight_layout()
        plt.savefig(f'{output_path}.svg')
        plt.close()

    _plot_ratio(
        data,
        num_idx=2, denom_idx=0,
        output_path='/data/height_ratios',
        title='Unlabeled Height relative to Control Height (median normalized and outliers capped at 1)',
        ylabel='Unlabeled height / Control height',
        cap_value=1
    )

    _plot_ratio(
        data,
        num_idx=3, denom_idx=1,
        output_path='/data/volume_ratios',
        title='Unlabeled Volume relative to Control Volume (median normalized and outliers capped at 1)',
        ylabel='Unlabeled volume / Control volume',
        cap_value=1
    )

def save_color_csv(
    ratios: list, # List of ratios
    colors: list, # List of colors corresponding to ratios
    output_path: str
) -> None:

    output_data = ['peak number, color category, value']
    for color, ratioidx in zip(colors, range(len(colors))):
        if color == 'green':
            continue
        elif color == 'yellow':
            colour_out = '>= 0.8'
        elif color == 'red':
            colour_out = 'lowest 8'
        output_data.append((f'{ratioidx}, {colour_out}, {ratios[ratioidx]}'))

    output_data = sorted(output_data[1:], key=lambda x: float(x.split(',')[2]))

    with open(output_path, 'w') as f:
        f.write('\n'.join(output_data))



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

def main():
    json_paths = ["/data/control.json", "/data/unlabelled.json"]

    data = load_data(json_paths)
    scaled_data = scale_data(data)

    height_data, volume_data = plot_data_ratios(scaled_data)

    cross_validated_data = cross_validate(height_data, volume_data)

    print(cross_validated_data)

    plot_cross_validated_data(cross_validated_data)

    save_data(cross_validated_data, "/data/cross_validated_data.json")
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

def plot_data_ratios(
    data: dict # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
) -> list:
    import numpy as np
    import matplotlib.pyplot as plt

    # Extracted helper to avoid repetition
    def _plot_ratio(data, num_idx, denom_idx, output_path, title, ylabel, cap_value=None):
        # Compute ratios
        ratios = [values[num_idx] / values[denom_idx] for values in data.values()]

        print(np.median(ratios))

        # Determine threshold as 9th lowest ratio (8 phenylalanine peaks, so below the 8 lowest ratios should be red)
        threshold = sorted(ratios)[8] 

        if cap_value is not None:
            for i in range(len(ratios)):
                if ratios[i] > cap_value:
                    ratios[i] = cap_value

        colors = ['red' if r < threshold else 'orange' if r < 0.8 else 'green' for r in ratios]

        plt.figure(figsize=(10, 6))
        plt.bar(range(len(ratios)), ratios, color=colors, width=1.0, align='center', edgecolor='none', linewidth=0)
        plt.xlim(0, len(ratios))
        plt.margins(x=0)
        plt.xlabel('Peak ID')
        plt.ylabel(ylabel)
        plt.title(title)

        red_count = colors.count('red')
        orange_count = colors.count('orange')
        green_count = colors.count('green')
        plt.text(0.5, 0.97, f'Red: {red_count}, orange: {orange_count}, Green: {green_count}', ha='center', va='center', transform=plt.gca().transAxes)
        plt.tight_layout()
        plt.savefig(f'{output_path}.svg')
        plt.close()

        output_data = {}
        for color, peakid, ratio in zip(colors, data.keys(), ratios):
            if color == 'green':
                continue
            output_data[peakid] = [color, ratio]

        return output_data

    height_data = _plot_ratio(
        data,
        num_idx=2, denom_idx=0,
        output_path='/data/height_ratios',
        title='Phe-Reverse Labelled Height relative to Control Height (median normalized and outliers capped at 1)',
        ylabel='Phe-Reverse Labelled height / Control height',
        cap_value=1
    )

    volume_data = _plot_ratio(
        data,
        num_idx=3, denom_idx=1,
        output_path='/data/volume_ratios',
        title='Phe-Reverse Labelled Volume relative to Control Volume (median normalized and outliers capped at 1)',
        ylabel='Phe-Reverse Labelled volume / Control volume',
        cap_value=1
    )

    return height_data, volume_data

def save_data(
    data: dict, # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
    output_path: str
) -> None:
    # Save data as json
    import json
    with open(output_path, 'w') as f:
        # Make readable with indent
        json.dump(data, f, indent=1)

    # Also save as csv for easier manual inspection
    import csv
    with open(output_path.replace('.json', '.csv'), 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['Peak ID', 'A Height', 'A Volume', 'B Height', 'B Volume'])
        for peak_id, values in data.items():
            csv_writer.writerow([peak_id] + values)

def cross_validate(
    height_data: dict, # Dict of "peak number: [color, height ratio]"
    volume_data: dict # Dict of "peak number: [color, volume ratio]"
) -> dict:
    output = {} # Structure: {peak_num: "height_ratio, height_colour, volume_ratio, volume_colour, confidence"}

    peaks = set(height_data.keys()).union(set(volume_data.keys()))
    for peak_num in peaks:
        if peak_num not in volume_data:
            confidence = "LOW"
            volume_data[peak_num] = ["none", 1]
        elif peak_num not in height_data:
            confidence = "LOW"
            height_data[peak_num] = ["none", 1]
        else:
            colors = [height_data[peak_num][0], volume_data[peak_num][0]]
            if "red" and "orange" in colors:
                confidence = "MEDIUM"
            elif "red" in colors:
                confidence = "HIGH"

        output[peak_num] = [height_data[peak_num][1], height_data[peak_num][0], volume_data[peak_num][1], volume_data[peak_num][0], confidence]

    # Sort output first by confidence, then by peak number
    confidence_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    output = dict(sorted(output.items(), key=lambda item: (confidence_order[item[1][4]], item[0])))

    return output

def plot_cross_validated_data(
    cross_validated_data: dict # Dict of "peak number: [height_ratio, height_colour, volume_ratio, volume_colour, confidence]"
) -> None:
    import matplotlib.pyplot as plt

    # Extract data for plotting
    peak_nums = list(cross_validated_data.keys())
    height_ratios = [cross_validated_data[peak_num][0] for peak_num in peak_nums]
    volume_ratios = [cross_validated_data[peak_num][2] for peak_num in peak_nums]

    # Red for HIGH, orange for MEDIUM, grey for LOW
    colors = ['red' if cross_validated_data[peak_num][4] == "HIGH" else 'orange' if cross_validated_data[peak_num][4] == "MEDIUM" else 'grey' for peak_num in peak_nums]

    plt.figure(figsize=(10, 6))
    plt.scatter(height_ratios, volume_ratios, c=colors)
    # Label each point with its peak number
    for i, peak_num in enumerate(peak_nums):
        plt.text(height_ratios[i], volume_ratios[i], str(peak_num), fontsize=8, ha='right')
    plt.xlabel('Height Ratio')
    plt.ylabel('Volume Ratio')
    plt.title('Cross-Validated Height and Volume Ratios')
    red_count = colors.count('red')
    orange_count = colors.count('orange')
    grey_count = colors.count('grey')
    plt.legend(handles=[plt.Line2D([0], [0], marker='o', color='w', label=f'HIGH: {red_count}', markerfacecolor='red', markersize=10),
                        plt.Line2D([0], [0], marker='o', color='w', label=f'MEDIUM: {orange_count}', markerfacecolor='orange', markersize=10),
                        plt.Line2D([0], [0], marker='o', color='w', label=f'LOW: {grey_count}', markerfacecolor='grey', markersize=10)],
               loc='upper right', title='Confidence Level')
    plt.grid()
    plt.tight_layout()
    plt.savefig('/data/cross_validated_ratios.svg')
    plt.close()


if __name__ == "__main__":
    main()

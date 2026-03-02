def load_data(json_paths: list) -> dict:  # List of paths to json files
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


def save_data(
    data: dict,  # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
    output_path: str,
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
        csv_writer.writerow(
            ['Peak ID', 'A Height', 'A Volume', 'B Height', 'B Volume']
        )
        for peak_id, values in data.items():
            csv_writer.writerow([peak_id] + values)


def combine_data(data_list: list) -> dict:  # List of dicts

    data_a, data_b = data_list
    combined_data = {}

    # Output data dict structure:
    # {peak_id: [A_height, A_volume, B_height, B_volume], ...}
    for peak_id in set(data_a.keys()).union(set(data_b.keys())):
        a_height, a_volume = data_a.get(peak_id, (None, None))
        b_height, b_volume = data_b.get(peak_id, (None, None))
        if 'None' in [a_height, a_volume, b_height, b_volume]:
            continue
        combined_data[peak_id] = [
            float(a_height),
            float(a_volume),
            float(b_height),
            float(b_volume),
        ]

    return combined_data

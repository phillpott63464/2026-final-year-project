def load_data(json_paths: list) -> dict:  # List of paths to json files
    data_list = []
    for json_path in json_paths:
        data_list.append(load_json(json_path))

    return combine_data(data_list)


def combine_data(data_list: list) -> dict:  # List of dicts
    # Combine data from multiple dicts into one dict with structure {peak_id: {A_height: float, A_volume: float, B_height: float, B_volume: float}, ...}

    data_a, data_b = data_list
    combined_data = {}

    # Output data dict structure:
    # {peak_id: {A_height, A_volume, B_height, B_volume}, ...}
    for peak_id in set(data_a.keys()).union(set(data_b.keys())):
        a_height = data_a.get(peak_id)['height']
        a_volume = data_a.get(peak_id)['volume']
        b_height = data_b.get(peak_id)['height']
        b_volume = data_b.get(peak_id)['volume']
        if 'None' in [a_height, a_volume, b_height, b_volume]:
            continue
        combined_data[peak_id] = {
            'A_height': float(a_height),
            'A_volume': float(a_volume),
            'B_height': float(b_height),
            'B_volume': float(b_volume),
        }

    return combined_data


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
        result[peak_num] = {'height': height, 'volume': volume}

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

    keys = list(data[list(data.keys())[0]].keys())
    keys_write = ['peak_id'] + keys

    # Also save as csv for easier manual inspection
    import csv

    with open(output_path.replace('.json', '.csv'), 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(
            keys_write
        )
        for peak_id, values in data.items():
            values = [values[k] for k in keys]
            csv_writer.writerow([peak_id] + values)

    # Also save as .md table for easy porting to reports
    with open(output_path.replace('.json', '.md'), 'w') as f:
        f.write('|{a}|\n'.format(a=' | '.join(keys_write)))
        f.write('|{a}|\n'.format(a=' | '.join(['---'] * len(keys_write))))
        for peak_id, values in data.items():
            values = [values[k] for k in keys]
            f.write(f'| {peak_id} | ' + ' | '.join(map(str, values)) + ' |\n')


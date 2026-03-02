import numpy as np


def cross_validate(
    height_data: dict,  # Dict of "peak number: [color, height ratio]"
    volume_data: dict,  # Dict of "peak number: [color, volume ratio]"
) -> dict:
    output = (
        {}
    )   # Structure: {peak_num: "height_ratio, height_colour, volume_ratio, volume_colour, confidence"}

    peaks = set(height_data.keys()).union(set(volume_data.keys()))
    for peak_num in peaks:
        if peak_num not in volume_data:
            confidence = 'LOW'
            volume_data[peak_num] = ['none', 1]
        elif peak_num not in height_data:
            confidence = 'LOW'
            height_data[peak_num] = ['none', 1]
        else:
            colors = [height_data[peak_num][0], volume_data[peak_num][0]]
            if 'red' in colors and not 'orange' in colors:
                confidence = 'HIGH'
            elif 'red' in colors or 'orange' in colors:
                confidence = 'MEDIUM'

        output[peak_num] = [
            height_data[peak_num][1],
            height_data[peak_num][0],
            volume_data[peak_num][1],
            volume_data[peak_num][0],
            confidence,
        ]

    # Sort output first by confidence, then by peak number
    confidence_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    output = dict(
        sorted(
            output.items(),
            key=lambda item: (confidence_order[item[1][4]], item[0]),
        )
    )

    return output


def get_mass_spec_incorporation_fractions() -> (float, float):
    mw = 29440.4
    n_count = 357
    n_terminus = 131   # Methionine

    mass_spec_labelled_peak = 29660.4
    mass_spec_unlabelled_peak = 29591.9

    i_labelled = (mass_spec_labelled_peak - mw + n_terminus) / n_count
    i_unlabelled = (mass_spec_unlabelled_peak - mw + n_terminus) / n_count

    print(f'Labelled incorporation fraction: {i_labelled:.6f}')
    print(f'Unlabelled incorporation fraction: {i_unlabelled:.6f}')
    return (i_labelled, i_unlabelled)


def get_nmr_ratios(nmr_data: dict) -> (float, float):

    a_heights = []
    a_volumes = []
    b_heights = []
    b_volumes = []

    for _, values in nmr_data.items():
        a_heights.append(values[0])
        b_heights.append(values[2])
        a_volumes.append(values[1])
        b_volumes.append(values[3])

    height_ratios = [b / a for a, b in zip(a_heights, b_heights) if a != 0]
    q1 = np.percentile(height_ratios, 25)
    q3 = np.percentile(height_ratios, 75)
    height_ratio = np.median([r for r in height_ratios if q1 <= r <= q3])

    volume_ratios = [x / y for x, y in zip(b_volumes, a_volumes)]
    q1 = np.percentile(volume_ratios, 25)
    q3 = np.percentile(volume_ratios, 75)
    volume_ratio = np.median([r for r in volume_ratios if q1 <= r <= q3])

    return height_ratio, volume_ratio


def scale_data(
    data: dict,  # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
) -> dict:
    import numpy as np

    scaled_B_heights = []
    scaled_B_volumes = []
    for peak_id, values in data.items():
        temp = values[2] / values[0]   # B_height / A_height
        temp2 = values[3] / values[1]   # B_volume / A_volume
        scaled_B_heights.append(temp)   # Scale B_height
        scaled_B_volumes.append(temp2)   # Scale B_volume

    # Median of scaled B
    median_B_height = np.median(scaled_B_heights)
    median_B_volume = np.median(scaled_B_volumes)

    # Scale B to median
    for peak_id, values in data.items():
        data[peak_id][2] = (
            values[2] / median_B_height
        )  # Scale B_height to match A
        data[peak_id][3] = (
            values[3] / median_B_volume
        )  # Scale B_volume to match A

    return data

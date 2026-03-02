from modules.calc import (
    get_nmr_ratios,
    scale_data,
    cross_validate,
    calculate_data_ratios,
    get_mass_spec_incorporation_fractions,
    estimate_incorporation,
)
from modules.io import load_data, save_data
from modules.plot import plot_data_ratios, plot_cross_validated_data


def main():
    json_paths = ['/data/control.json', '/data/unlabelled.json']

    process_nmr_data(json_paths)
    process_mass_spec_data(json_paths)


def process_nmr_data(json_paths: list) -> None:
    data = load_data(json_paths)
    scaled_data = scale_data(data)

    height_full, volume_full, height_data, volume_data = calculate_data_ratios(
        scaled_data
    )

    cross_validated_data = cross_validate(height_data, volume_data)

    plot_cross_validated_data(cross_validated_data)
    plot_data_ratios(height_full, volume_full)
    save_data(cross_validated_data, '/data/cross_validated_data.json')
    save_data(scaled_data, '/data/scaled_data.json')


def process_mass_spec_data(json_paths: list) -> None:
    nmr_data = load_data(json_paths)
    height_ratio, volume_ratio = get_nmr_ratios(nmr_data)
    i_a, i_b = get_mass_spec_incorporation_fractions()

    estimate_incorporation(height_ratio, volume_ratio, i_a, i_b)


if __name__ == '__main__':
    main()

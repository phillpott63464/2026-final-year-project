from modules.calc import (
    get_nmr_ratios,
    scale_data,
    cross_validate,
    get_mass_spec_incorporation_fractions,
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

    height_data, volume_data = plot_data_ratios(scaled_data) # Probably need to separate out those functions

    cross_validated_data = cross_validate(height_data, volume_data)

    plot_cross_validated_data(cross_validated_data)

    save_data(cross_validated_data, '/data/cross_validated_data.json')
    save_data(scaled_data, '/data/scaled_data.json')


def process_mass_spec_data(json_paths: list) -> None:
    nmr_data = load_data(json_paths)
    height_ratio, volume_ratio = get_nmr_ratios(nmr_data)
    i_a, i_b = get_mass_spec_incorporation_fractions()

    # We assume that peak intensity is proportional the number of nitrogens
    # Number of nitrogens = incorporation fraction * sample concentration
    # Therefore signal_a = concentration_a x incorporation_a, signal_b = concentration_b x incorporation_b
    # We are calculating signal_b / signal_a
    # This expands to (concentration_b * incorporation_b) / (concentration_a * incorporation_a)
    # We have those values, so we can calculate expected signal ratio
    c_a = 260.08   # μM but units cancel out
    c_b = 232.71

    print(f'Calculated signal ratio: {(c_b * i_b) / (c_a * i_a):.6f}')
    print(f'height_ratio: {height_ratio:.6f}')
    print(f'volume_ratio: {volume_ratio:.6f}')

    # Not great results
    # But we'll rearrange to estimate incorporation_b anyway

    print(
        f'Estimated incorporation fraction for unlabelled sample (height): {(height_ratio * c_a * i_a) / c_b:.6f}'
    )
    print(
        f'Estimated incorporation fraction for unlabelled sample (volume): {(volume_ratio * c_a * i_a) / c_b:.6f}'
    )

    # Once again, not great


if __name__ == '__main__':
    main()

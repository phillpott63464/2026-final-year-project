import numpy as np
import matplotlib.pyplot as plt


def plot_cross_validated_data(
    cross_validated_data: dict,  # Dict of "peak number: [height_ratio, height_colour, volume_ratio, volume_colour, confidence]"
) -> None:

    # Extract data for plotting
    peak_nums = list(cross_validated_data.keys())
    height_ratios = [
        cross_validated_data[peak_num][0] for peak_num in peak_nums
    ]
    volume_ratios = [
        cross_validated_data[peak_num][2] for peak_num in peak_nums
    ]

    # Red for HIGH, orange for MEDIUM, grey for LOW
    colors = [
        'red'
        if cross_validated_data[peak_num][4] == 'HIGH'
        else 'orange'
        if cross_validated_data[peak_num][4] == 'MEDIUM'
        else 'grey'
        for peak_num in peak_nums
    ]

    plt.figure(figsize=(10, 6))
    plt.scatter(height_ratios, volume_ratios, c=colors)
    # Label each point with its peak number
    for i, peak_num in enumerate(peak_nums):
        plt.text(
            height_ratios[i],
            volume_ratios[i],
            str(peak_num),
            fontsize=8,
            ha='right',
        )
    plt.xlabel('Height Ratio')
    plt.ylabel('Volume Ratio')
    plt.title('Cross-Validated Height and Volume Ratios')
    red_count = colors.count('red')
    orange_count = colors.count('orange')
    grey_count = colors.count('grey')
    plt.legend(
        handles=[
            plt.Line2D(
                [0],
                [0],
                marker='o',
                color='w',
                label=f'HIGH: {red_count}',
                markerfacecolor='red',
                markersize=10,
            ),
            plt.Line2D(
                [0],
                [0],
                marker='o',
                color='w',
                label=f'MEDIUM: {orange_count}',
                markerfacecolor='orange',
                markersize=10,
            ),
            plt.Line2D(
                [0],
                [0],
                marker='o',
                color='w',
                label=f'LOW: {grey_count}',
                markerfacecolor='grey',
                markersize=10,
            ),
        ],
        loc='upper right',
        title='Confidence Level',
    )
    plt.grid()
    plt.tight_layout()
    plt.savefig('/data/cross_validated_ratios.svg')
    plt.close()


def plot_data_ratios(
    data: dict,  # Dict {peak_id: [A_height, A_volume, B_height, B_volume], ...}
) -> list:

    # Extracted helper to avoid repetition
    def _plot_ratio(
        data, num_idx, denom_idx, output_path, title, ylabel, cap_value=None
    ):
        # Compute ratios
        ratios = [
            values[num_idx] / values[denom_idx] for values in data.values()
        ]

        # Determine threshold as 9th lowest ratio (8 phenylalanine peaks, so below the 8 lowest ratios should be red)
        threshold = sorted(ratios)[8]

        if cap_value is not None:
            for i in range(len(ratios)):
                if ratios[i] > cap_value:
                    ratios[i] = cap_value

        colors = [
            'red' if r < threshold else 'orange' if r < 0.8 else 'green'
            for r in ratios
        ]

        plt.figure(figsize=(10, 6))
        plt.bar(
            range(len(ratios)),
            ratios,
            color=colors,
            width=1.0,
            align='center',
            edgecolor='none',
            linewidth=0,
        )
        plt.xlim(0, len(ratios))
        plt.margins(x=0)
        plt.xlabel('Peak ID')
        plt.ylabel(ylabel)
        plt.title(title)

        red_count = colors.count('red')
        orange_count = colors.count('orange')
        green_count = colors.count('green')
        plt.text(
            0.5,
            0.97,
            f'Red: {red_count}, orange: {orange_count}, Green: {green_count}',
            ha='center',
            va='center',
            transform=plt.gca().transAxes,
        )
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
        num_idx=2,
        denom_idx=0,
        output_path='/data/height_ratios',
        title='Phe-Reverse Labelled Height relative to Control Height (median normalized and outliers capped at 1)',
        ylabel='Phe-Reverse Labelled height / Control height',
        cap_value=1,
    )

    volume_data = _plot_ratio(
        data,
        num_idx=3,
        denom_idx=1,
        output_path='/data/volume_ratios',
        title='Phe-Reverse Labelled Volume relative to Control Volume (median normalized and outliers capped at 1)',
        ylabel='Phe-Reverse Labelled volume / Control volume',
        cap_value=1,
    )

    return height_data, volume_data

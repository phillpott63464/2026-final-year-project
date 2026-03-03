import numpy as np
import matplotlib.pyplot as plt


def plot_cross_validated_data(
    cross_validated_data: dict,  # Dict of "peak number: {height_ratio: float, height_colour: str, volume_ratio: float, volume_colour: str, confidence: str}"
) -> None:

    # Extract data for plotting
    peak_nums = list(cross_validated_data.keys())
    height_ratios = [
        cross_validated_data[peak_num]['height_ratio'] for peak_num in peak_nums
    ]
    height_colours = [
        cross_validated_data[peak_num]['height_colour'] for peak_num in peak_nums
    ]
    volume_ratios = [
        cross_validated_data[peak_num]['volume_ratio'] for peak_num in peak_nums
    ]
    volume_colours = [
        cross_validated_data[peak_num]['volume_colour'] for peak_num in peak_nums
    ]

    # Red for HIGH, orange for MEDIUM, grey for LOW
    colors = [
        'red'
        if cross_validated_data[peak_num]['confidence'] == 'HIGH'
        else 'orange'
        if cross_validated_data[peak_num]['confidence'] == 'MEDIUM'
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
    height_data: dict,  # Dict {peak_id: [color, ratio], ...}
    volume_data: dict,  # Dict {peak_id: [color, ratio], ...}
) -> None:
    def _plot_from_dict(data, output_path, title, ylabel):
        peak_ids = list(data.keys())
        ratios = [data[p][1] for p in peak_ids]
        colors = [data[p][0] for p in peak_ids]

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
        plt.savefig(output_path)
        plt.close()

    _plot_from_dict(
        height_data,
        '/data/height_ratios.svg',
        'Phe-Reverse Labelled Height relative to Control Height (median normalized and outliers capped at 1)',
        'Phe-Reverse Labelled height / Control height',
    )

    _plot_from_dict(
        volume_data,
        '/data/volume_ratios.svg',
        'Phe-Reverse Labelled Volume relative to Control Volume (median normalized and outliers capped at 1)',
        'Phe-Reverse Labelled volume / Control volume',
    )

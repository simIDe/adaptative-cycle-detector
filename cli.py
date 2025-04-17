# cycle_detector/cli.py

import os
import click
from detection import detect_cycles
from cycles_utils import *


@click.command()
@click.option('--data-path', '-d', type=click.Path(exists=True), required=True, help='Path to the data directory.')
@click.option('--output-dir', '-o', type=click.Path(), default='output', help='Directory to save cycle detection results.')
@click.option('--fs', '-f', type=float, required=True, help='Sampling frequency in Hz.')
@click.option('--pattern', '-pat', type=click.Choice(['on_peak', 'between_peak', 'both'], case_sensitive=False), default='both', help='Detection pattern.')
@click.option('--data-source', '-s', type=str, required=True, help='Data source keyword to filter files (e.g., "c3d", "xsens", "lea").')
@click.option('--condition', '-c', type=str, required=True, help='Experimental condition keyword to filter files (e.g., "nuqueflexion", "tronflexion").')
@click.option('--position-col', '-pos', type=str, required=True, help='Name of the position column in the data.')
@click.option('--signal', '-sig', type=click.Choice(['position', 'velocity', 'abs_velocity'], case_sensitive=False), default='abs_velocity', help='Signal to use for cycle detection.')
@click.option('--threshold', '-t', type=float, help='Threshold value for cycle detection.')
@click.option('--distance', '-dist', type=float, help='Minimum peak distance in seconds.')
def main(data_path, output_dir, fs, pattern, data_source, condition, position_col, signal, threshold, distance):
    """
    Adaptive Cycle Detection Tool

    Processes experimental records to detect cycles with adjustable parameters.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load last used detection parameters
    detection_parameters = load_last_parameters(output_dir)
    # Override pattern if specified via CLI
    detection_parameters['pattern'] = pattern.lower()
    detection_parameters['signal'] = signal.lower()

    # Override threshold and distance if specified via CLI
    if threshold is not None:
        detection_parameters['threshold'] = threshold
    if distance is not None:
        detection_parameters['distance'] = distance

    # List all CSV and Parquet files in the data directory that match the data_source and condition filters
    records = [
        os.path.join(data_path, f)
        for f in os.listdir(data_path)
        if f.lower().endswith(('.csv', '.parquet')) and data_source.lower() in f.lower() and condition.lower() in f.lower()
    ]

    if not records:
        click.secho(
            "No CSV or Parquet records found matching the specified data source and condition.", fg='red')
        return

    for record_path in records:
        record_name = os.path.splitext(os.path.basename(record_path))[0]

        try:
            if has_been_processed(record_name, output_dir):
                click.secho(
                    f"Record '{record_name}' has already been processed.", fg='yellow')
                reprocess = click.prompt(
                    "Do you want to reprocess it? (Y/N)", default='N', show_default=True)
                if reprocess.strip().lower() != 'y':
                    continue

            click.secho(f"Processing record: {record_name}", fg='green')

            # Load and prepare data
            data = load_data(record_path)
            filename = os.path.basename(record_path)
            prepared_data = prepare_data_for_cycle_detection(
                data, filename, fs=fs, data_source=data_source.lower(), condition=condition.lower(), position_col=position_col
            )

            # Interactive detection and adjustment loop
            while True:
                try:
                    sep_indices = detect_cycles(
                        prepared_data,
                        threshold=detection_parameters['threshold'],
                        distance=detection_parameters['distance'],
                        pattern=detection_parameters['pattern'],
                        signal=detection_parameters['signal'],
                        fs=fs
                    )
                    show_plots(
                        prepared_data['Position'],
                        prepared_data.get('Velocity', None),
                        sep_indices,
                        detection_parameters['threshold'],
                        signal=detection_parameters['signal']
                    )
                except ValueError as e:
                    click.secho(f"Detection Error: {str(e)}", fg='red')

                accept = click.prompt(
                    "Are the detection results acceptable? (Y/N)", default='Y', show_default=True)
                if accept.strip().lower() == 'y':
                    break
                else:
                    # Adjust parameters
                    detection_parameters['threshold'] = click.prompt(
                        "Enter new threshold value",
                        type=float,
                        default=detection_parameters['threshold'],
                        show_default=True
                    )
                    detection_parameters['distance'] = click.prompt(
                        "Enter new peak distance (in seconds)",
                        type=float,
                        default=detection_parameters['distance'],
                        show_default=True
                    )
                    detection_parameters['pattern'] = click.prompt(
                        "Enter pattern",
                        type=click.Choice(
                            ['on_peak', 'between_peak', 'both'], case_sensitive=False),
                        default=detection_parameters['pattern'],
                        show_default=True
                    )
                    manual = click.prompt(
                        "Do you want to perform manual cutting? (Y/N)", default='N', show_default=True)
                    if manual.strip().lower() == 'y':
                        sep_indices = manual_cutting(
                            prepared_data['Position'].values,
                            prepared_data.get('Velocity', None),
                            fs=fs
                        )
                        break  # Exit the adjustment loop

            # Save results
            save_cycle_data(record_name, detection_parameters,
                            sep_indices, output_dir)
            log_processed_record(record_name, output_dir, detection_parameters)

            # Save the current detection parameters as last used
            save_last_parameters(output_dir, detection_parameters)

        except Exception as e:
            click.secho(
                f"Error processing '{record_name}': {str(e)}", fg='red')
            continue  # Skip to next record

    click.secho("Processing completed for all records.", fg='green')


if __name__ == '__main__':
    main()

# cycle_detector/utils.py

import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import click
from datetime import datetime
import csv
import re


def load_data(record_path: str) -> pd.DataFrame:
    """
    Load data from a CSV or Parquet file.

    Parameters:
        record_path (str): Path to the CSV or Parquet file.

    Returns:
        pd.DataFrame: Loaded data.
    """
    try:
        if record_path.lower().endswith('.csv'):
            data = pd.read_csv(record_path)
        elif record_path.lower().endswith('.parquet'):
            data = pd.read_parquet(record_path)
        else:
            raise ValueError(
                "Unsupported file format. Only .csv and .parquet are supported.")
        return data
    except Exception as e:
        raise ValueError(f"Failed to load data from {record_path}: {str(e)}")


def prepare_data_for_cycle_detection(data: pd.DataFrame, filename: str, fs: float = None, data_source: str = '', condition: str = '', position_col: str = '', velocity_col: str = '') -> pd.DataFrame:
    """
    Prepare data for cycle detection by selecting necessary columns and adding attributes.
    Uses the specified position column.

    Parameters:
        data (pd.DataFrame): Raw data.
        filename (str): Name of the data file.
        fs (float, optional): Sampling frequency.
        data_source (str): Data source keyword (e.g., 'c3d', 'xsens', 'lea').
        condition (str): Experimental condition keyword (e.g., 'nuqueflexion', 'tronflexion').
        position_col (str): Name of the position column.
        velocity_col (str): Name of the velocity column.

    Returns:
        pd.DataFrame: Prepared data with necessary columns and attributes.
    """
    if not position_col:
        raise ValueError(
            "Position column name must be provided via --position-col option.")

    if position_col not in data.columns:
        raise ValueError(
            f"Position column '{position_col}' not found in data.")

    prepared = pd.DataFrame()
    prepared['Position'] = data[position_col]

    # Compute velocity if not provided
    if not velocity_col:
        prepared['Velocity'] = np.gradient(prepared['Position'])

    # Store sampling frequency as an attribute for later use
    # Default to 100 Hz if not provided
    if fs:
        prepared.attrs['fs'] = fs
    else:
        raise ValueError("Sampling frequency must be provided")

    # prepared["position"] = smooth_data_low_pass(prepared['Position'], , fs)
    # fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    # ax.plot(prepared['Velocity'])
    prepared["Position"] = smooth_data_low_pass(prepared['Position'], 2, fs)
    prepared["Velocity"] = smooth_data_low_pass(prepared['Velocity'], 2, fs)
    # ax.plot(prepared['velocity'])
    # plt.show()

    return prepared

def smooth_data_low_pass(data: pd.Series, cutoff: float, fs: float) -> pd.Series:
    """
    Apply a low-pass filter to smooth the data.

    Parameters:
        data (pd.Series): Data to be smoothed.
        cutoff (float): Cutoff frequency for the low-pass filter.
        fs (float): Sampling frequency.

    Returns:
        pd.Series: Smoothed data.
    """
    from scipy.signal import butter, filtfilt

    # Normalize the cutoff frequency
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    print(f"normal_cutoff: {normal_cutoff}")

    # Design a low-pass Butterworth
    b, a = butter(1, normal_cutoff, btype='low', analog=False)

    # Apply the filter
    smoothed = filtfilt(b, a, data)

    return pd.Series(smoothed, index=data.index)



def save_cycle_data(record_name, detection_parameters, sep_indices, output_dir):
    """
    Save cycle detection results and parameters to a JSON file.

    Parameters:
        record_name (str): Name of the record.
        detection_parameters (dict): Parameters used for detection.
        sep_indices (np.ndarray): Detected cycle indices.
        output_dir (str): Directory to save the JSON file.
    """
    data = {
        "record_name": record_name,
        "detection_parameters": detection_parameters,
        "cycle_indices": sep_indices.tolist(),
        "timestamp": datetime.now().isoformat()
    }
    output_file = os.path.join(output_dir, f"{record_name}_cycles.json")
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        click.secho(f"Saved cycle data to {output_file}", fg='green')
    except Exception as e:
        raise IOError(
            f"Failed to save cycle data for '{record_name}': {str(e)}")


def has_been_processed(record_name, output_dir):
    """
    Check if a record has already been processed.

    Parameters:
        record_name (str): Name of the record.
        output_dir (str): Directory where results are saved.

    Returns:
        bool: True if processed, False otherwise.
    """
    output_file = os.path.join(output_dir, f"{record_name}_cycles.json")
    return os.path.isfile(output_file)


def log_processed_record(record_name, output_dir, detection_parameters):
    """
    Log the processed record with timestamp and parameters.

    Parameters:
        record_name (str): Name of the record.
        output_dir (str): Directory where the log is stored.
        detection_parameters (dict): Parameters used for detection.
    """
    log_file = os.path.join(output_dir, 'processed_records.log')
    try:
        with open(log_file, 'a', newline='') as csvfile:
            log_writer = csv.writer(csvfile)
            timestamp = datetime.now().isoformat()
            parameters_file = f"{record_name}_cycles.json"
            log_writer.writerow(
                [record_name, timestamp, parameters_file, json.dumps(detection_parameters)])
    except Exception as e:
        click.secho(
            f"Failed to log processed record '{record_name}': {str(e)}", fg='red')


def show_plots(position, velocity, sep_indices, threshold, manual_cuts=None, signal='position'):
    """
    Plot the position and velocity data with detected cycle boundaries.

    Parameters:
        position (np.ndarray): Position data.
        velocity (np.ndarray or None): Velocity data.
        sep_indices (np.ndarray): Detected cycle indices.
        threshold (float): Threshold used for detection.
        manual_cuts (np.ndarray or None): Manually defined cycle indices.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    if signal == 'position':
        treshold_axis = 0
    elif signal == 'velocity' or signal == 'abs_velocity':
        treshold_axis = 1
    
    if signal == 'abs_velocity':
        velocity = np.abs(velocity)

    axes[0].plot(position, label='Position')
    if threshold != 0:
        axes[treshold_axis].axhline(threshold, color='r',
                        linestyle='--', label='Threshold')
    for idx in sep_indices:
        axes[0].axvline(idx, color='k', linestyle=':', alpha=0.7)
    if manual_cuts is not None and len(manual_cuts) > 0:
        for idx in manual_cuts:
            axes[0].axvline(idx, color='m', linestyle='-',
                            alpha=0.9, label='Manual Cut')
    axes[0].set_title('Position Data with Detected Cycles')
    axes[0].legend()
    axes[0].grid(True)

    if velocity is not None:
        axes[1].plot(velocity, label='Velocity', color='g')
        for idx in sep_indices:
            axes[1].axvline(idx, color='k', linestyle=':', alpha=0.7)
        if manual_cuts is not None and len(manual_cuts) > 0:
            for idx in manual_cuts:
                axes[1].axvline(idx, color='m', linestyle='-',
                                alpha=0.9, label='Manual Cut')
        axes[1].set_title('Velocity Data with Detected Cycles')
        axes[1].legend()
        axes[1].grid(True)

    plt.tight_layout()
    plt.show(block=False)


def manual_cutting(position, velocity, fs, confirmation=True) -> np.ndarray:
    """
    Allow users to manually define cycle boundaries via interactive plots.
    After manual cutting, render the cuts and allow validation or restart.

    Parameters:
        position (np.ndarray): Position data.
        velocity (np.ndarray or None): Velocity data.
        fs (float): Sampling frequency.
        confirmation (bool): Whether to confirm the manual cuts.

    Returns:
        np.ndarray: Manually defined cycle indices.
    """
    while True:
        sep_indices = []

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        ax1.plot(position, label='Position', color='blue')
        if velocity is not None:
            ax2.plot(velocity, label='Velocity', color='green')
        ax1.set_title('Manual Cycle Cutting - Click to define cycle boundaries')
        ax1.legend()
        ax1.grid(True)

        click.secho(
            "Please click on the plot to define cycle boundaries. Close the plot when done.", fg='cyan')

        points = plt.ginput(n=-1, timeout=0)  # Wait for user to close the plot
        sep_indices = [int(x[0]) for x in points]

        plt.close(fig)

        if not sep_indices:
            click.secho("No points selected. Please try again.", fg='yellow')
            continue

        # Render the cuts for validation
        click.secho("Rendering the manual cuts for validation...", fg='cyan')
        show_plots(position, velocity, sep_indices,
                   threshold=0, manual_cuts=sep_indices)

        # Prompt user to validate or restart manual cutting
        validate = click.prompt(
            "Are the manual cuts acceptable? (Y/N)", default='Y', show_default=True)
        if validate.strip().lower() == 'y':
            break
        else:
            click.secho("Restarting manual cutting process.", fg='yellow')

    return np.array(sep_indices)


def save_last_parameters(output_dir, detection_parameters):
    """
    Save the last used detection parameters to a JSON file.

    Parameters:
        output_dir (str): Directory where to save the parameters file.
        detection_parameters (dict): Parameters to save.
    """
    last_params_file = os.path.join(output_dir, 'last_parameters.json')
    try:
        with open(last_params_file, 'w') as f:
            json.dump(detection_parameters, f, indent=4)
        click.secho(
            f"Saved last detection parameters to {last_params_file}", fg='green')
    except Exception as e:
        raise IOError(f"Failed to save last detection parameters: {str(e)}")


def load_last_parameters(output_dir):
    """
    Load the last used detection parameters from a JSON file.

    Parameters:
        output_dir (str): Directory where the parameters file is saved.

    Returns:
        dict: Last used detection parameters or default values.
    """
    last_params_file = os.path.join(output_dir, 'last_parameters.json')
    if os.path.isfile(last_params_file):
        try:
            with open(last_params_file, 'r') as f:
                detection_parameters = json.load(f)
            click.secho(
                f"Loaded last detection parameters from {last_params_file}", fg='green')
            return detection_parameters
        except Exception as e:
            click.secho(
                f"Failed to load last detection parameters: {str(e)}", fg='red')
    # Return default parameters if loading fails or file doesn't exist
    return {
        'threshold': 1.0,
        'distance': 2.0,
        'pattern': 'both'
    }

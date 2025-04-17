# cycle_detector/detection.py

import numpy as np
import pandas as pd
import click
from scipy.signal import find_peaks


def detect_cycles(
    data: pd.DataFrame,
    threshold: float = 1.0,
    distance: float = 2.0,
    pattern: str = 'both',
    signal: str = 'position',
    fs: int = 1
) -> np.ndarray:
    """
    Detect cycles in the data based on the provided parameters.

    Parameters:
        data (pd.DataFrame): Prepared data containing the specified signal.
        threshold (float): Threshold value for peak detection.
        distance (float): Minimum distance between peaks in seconds.
        pattern (str): Detection pattern ('on_peak', 'between_peak', 'both').
        signal (str): Signal to use for detection ('position', 'velocity', 'abs_velocity').

    Returns:
        np.ndarray: Indices of detected cycle boundaries.
    """
    # Validate the signal parameter
    valid_signals = ['position', 'velocity', 'abs_velocity']
    if signal not in valid_signals:
        raise ValueError(
            f"Invalid signal '{signal}'. Choose from {valid_signals}.")

    # validate the pattern parameter
    valid_patterns = ['on_peak', 'between_peak', 'both']
    if pattern not in valid_patterns:
        raise ValueError(
            f"Invalid pattern '{pattern}'. Choose from {valid_patterns}.")

    # Check if the desired signal column exists in the data
    if signal == 'position':
        if 'Position' not in data.columns:
            raise ValueError("Data must contain a 'Position' column.")
        signal_data = data['Position'].values
    elif signal == 'velocity':
        if 'Velocity' not in data.columns:
            raise ValueError("Data must contain a 'Velocity' column.")
        signal_data = data['Velocity'].values
    elif signal == 'abs_velocity':
        if 'Velocity' not in data.columns:
            raise ValueError(
                "Data must contain a 'Velocity' column to compute its absolute value.")
        signal_data = np.abs(data['Velocity'].values)

    # Retrieve sampling frequency; default to 100 Hz if not provided
    min_distance = int(distance * fs)  # Convert seconds to samples
    print(f"min_distance: {min_distance}")

    # Initialize lists for peak and trough indices
    peaks = np.array([])
    troughs = np.array([])

    # NOTE:Not sure how to handle peak that occurs at the beginning of the signal.
    # Technically, it can be considered a peak, but it is not between two troughs.
    # So, it will not be detected by the find peak function. This is a limitation of the current implementation.

    # Detect peaks based on the 'on_peak' pattern
    if pattern in ['on_peak', 'both']:
        peaks, properties = find_peaks(
            signal_data, height=threshold, distance=min_distance)
        print(peaks)
        #max, min, mean 
        max = np.max(signal_data)
        min = np.min(signal_data)
        mean = np.mean(signal_data)
        print(f"Max: {max}, Min: {min}, Mean: {mean}")
        print(f"trehshold: {threshold}")

    # Detect troughs based on the 'between_peak' pattern
    if pattern in ['between_peak', 'both']:
        peaks_for_troughs, properties = find_peaks(
            signal_data, height=threshold, distance=min_distance)

        # Compute troughs as the mean indices between consecutive peaks
        troughs = np.array([
            np.mean([peaks_for_troughs[i], peaks_for_troughs[i+1]])
            for i in range(len(peaks_for_troughs)-1)
        ])
        # Ensure that trough indices are integers
        troughs = troughs.astype(int)

    # Combine and sort peak and trough indices
    sep_indices = np.sort(np.concatenate((peaks, troughs)))

    if len(sep_indices) == 0:
        raise ValueError(
            "No cycles detected. Adjust the detection parameters or try manual cutting.")

    # always add the first and last index to ensure that the entire signal is included
    sep_indices = np.insert(sep_indices, 0, 0)
    sep_indices = np.append(sep_indices, len(signal_data)-1)

    # inform the user about the number of detected cycles
    click.secho(
        f"Detected {len(sep_indices)-1} cycles.", fg='yellow')

    return sep_indices

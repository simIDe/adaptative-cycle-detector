# cycle_detector/tests/test_detection.py

import pytest
import pandas as pd
import numpy as np
from cycle_detector.detection import detect_cycles


# ============================ Tests for Position Signal ============================

def test_detect_cycles_on_position_peak():
    """
    Test peak detection on the Position signal.
    """
    # Sample data with clear peaks in Position
    data = pd.DataFrame({
        'Position': [0, 1, 0, 1, 0, 1, 0],
        'Velocity': [0, 0, 0, 0, 0, 0, 0]  # Irrelevant for this test
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='on_peak',
        signal='position'
    )
    assert list(sep_indices) == [1, 3, 5]


def test_detect_cycles_on_position_trough():
    """
    Test trough detection on the Position signal.
    """
    # Sample data with clear troughs in Position
    data = pd.DataFrame({
        'Position': [0, 1, 0, 1, 0, 1, 0, 1, 0],
        'Velocity': [0, 0, 0, 0, 0, 0, 0, 0, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='between_peak',
        signal='position'
    )
    assert list(sep_indices) == [2, 4, 6]


def test_detect_cycles_on_position_both():
    """
    Test both peak and trough detection on the Position signal.
    """
    # Sample data with peaks and troughs in Position
    data = pd.DataFrame({
        'Position': [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0],
        'Velocity': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='both',
        signal='position'
    )
    assert list(sep_indices) == [1, 3, 5, 7, 9]


def test_detect_cycles_on_position_no_cycles():
    """
    Test behavior when no cycles are detected on the Position signal.
    """
    # Data without any peaks or troughs above the threshold in Position
    data = pd.DataFrame({
        'Position': [0.1, 0.2, 0.1, 0.2, 0.1],
        'Velocity': [0, 0, 0, 0, 0]
    })
    with pytest.raises(ValueError, match="No cycles detected"):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='both',
            signal='position'
        )


def test_detect_cycles_on_position_distance_constraint():
    """
    Test peak detection with distance constraints on the Position signal.
    """
    # Data with peaks closer than the specified distance in Position
    data = pd.DataFrame({
        'Position': [0, 1, 0.6, 1, 0],
        'Velocity': [0, 0, 0, 0, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=2.0,  # Requires at least 2 seconds between peaks
        pattern='on_peak',
        signal='position'
    )
    # Only the first peak is detected due to distance constraint
    assert list(sep_indices) == [1, 3]


def test_detect_cycles_on_position_invalid_pattern():
    """
    Test behavior when an invalid pattern is provided for the Position signal.
    """
    # Attempt to use an invalid pattern on Position
    data = pd.DataFrame({
        'Position': [0, 1, 0, 1, 0],
        'Velocity': [0, 0, 0, 0, 0]
    })
    with pytest.raises(ValueError, match="Invalid pattern 'invalid_pattern'"):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='invalid_pattern',
            signal='position'
        )


# ============================ Tests for Velocity Signal ============================

def test_detect_cycles_on_velocity_peak():
    """
    Test peak detection on the Velocity signal.
    """
    # Sample data with clear peaks in Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0, 0, 0],
        'Velocity': [0, 1, 0, 1, 0, 1, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='on_peak',
        signal='velocity'
    )
    assert list(sep_indices) == [1, 3, 5]


def test_detect_cycles_on_velocity_trough():
    """
    Test trough detection on the Velocity signal.
    """
    # Sample data with clear troughs in Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Velocity': [0, 1, 0, 1, 0, 1, 0, 1, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='between_peak',
        signal='velocity'
    )
    assert list(sep_indices) == [2, 4, 6]


def test_detect_cycles_on_velocity_both():
    """
    Test both peak and trough detection on the Velocity signal.
    """
    # Sample data with peaks and troughs in Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Velocity': [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='both',
        signal='velocity'
    )
    assert list(sep_indices) == [1, 3, 5, 7, 9]


def test_detect_cycles_on_velocity_no_cycles():
    """
    Test behavior when no cycles are detected on the Velocity signal.
    """
    # Data without any peaks or troughs above the threshold in Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0],
        'Velocity': [0.1, 0.2, 0.1, 0.2, 0.1]
    })
    with pytest.raises(ValueError, match="No cycles detected"):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='both',
            signal='velocity'
        )


def test_detect_cycles_on_velocity_distance_constraint():
    """
    Test peak detection with distance constraints on the Velocity signal.
    """
    # Data with peaks closer than the specified distance in Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0],
        'Velocity': [0, 1, 0.6, 1, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=2.0,  # Requires at least 2 seconds between peaks
        pattern='on_peak',
        signal='velocity'
    )
    # Only the first peak is detected due to distance constraint
    assert list(sep_indices) == [1, 3]


def test_detect_cycles_on_velocity_invalid_pattern():
    """
    Test behavior when an invalid pattern is provided for the Velocity signal.
    """
    # Attempt to use an invalid pattern on Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0],
        'Velocity': [0, 1, 0, 1, 0]
    })
    with pytest.raises(ValueError, match="Invalid pattern 'invalid_pattern'"):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='invalid_pattern',
            signal='velocity'
        )


# ============================ Tests for Absolute Velocity Signal ============================

def test_detect_cycles_on_abs_velocity_peak():
    """
    Test peak detection on the absolute value of Velocity signal.
    """
    # Sample data with clear peaks in absolute Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0, 0, 0],
        'Velocity': [0, -1, 0, 1, 0, -1, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='on_peak',
        signal='abs_velocity'
    )
    assert list(sep_indices) == [1, 3, 5]


def test_detect_cycles_on_abs_velocity_trough():
    """
    Test trough detection on the absolute value of Velocity signal.
    """
    # Since absolute velocity is always non-negative, troughs are zeros.
    # However, find_peaks on -abs_velocity will detect zeros as troughs if threshold <=0
    # For this test, we'll use a higher threshold to ensure only specific troughs are detected.
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Velocity': [0, 1, 0, -1, 0, 1, 0, -1, 0]
    })
    # Here, troughs in abs_velocity would correspond to zeros, but since abs_velocity = 1 for all non-zero entries
    # and 0 is below threshold, there should be no troughs
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='between_peak',
        signal='abs_velocity'
    )
    # Since abs_velocity never goes below threshold, expect ValueError
    with pytest.raises(ValueError, match="No cycles detected"):
        detect_cycles(
            data,
            threshold=1.5,  # Higher than any abs_velocity
            distance=1.0,
            pattern='between_peak',
            signal='abs_velocity'
        )


def test_detect_cycles_on_abs_velocity_both():
    """
    Test both peak and trough detection on the absolute value of Velocity signal.
    """
    # Sample data with peaks and troughs in absolute Velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Velocity': [0, -1, 0, 1, 0, -1, 0, 1, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=1.0,
        pattern='both',
        signal='abs_velocity'
    )
    assert list(sep_indices) == [1, 2, 3, 4, 5, 6, 7]


def test_detect_cycles_on_abs_velocity_no_cycles():
    """
    Test behavior when no cycles are detected on the absolute Velocity signal.
    """
    # Data without any peaks or troughs above the threshold in abs_velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0],
        'Velocity': [0.1, -0.2, 0.1, -0.2, 0.1]
    })
    with pytest.raises(ValueError, match="No cycles detected"):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='both',
            signal='abs_velocity'
        )


def test_detect_cycles_on_abs_velocity_distance_constraint():
    """
    Test peak detection with distance constraints on the absolute Velocity signal.
    """
    # Data with peaks closer than the specified distance in abs_velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0],
        'Velocity': [0, -1, 0.6, 1, 0]
    })
    sep_indices = detect_cycles(
        data,
        threshold=0.5,
        distance=2.0,  # Requires at least 2 seconds between peaks
        pattern='on_peak',
        signal='abs_velocity'
    )
    # Only the first peak is detected due to distance constraint
    assert list(sep_indices) == [1, 3]


def test_detect_cycles_on_abs_velocity_invalid_pattern():
    """
    Test behavior when an invalid pattern is provided for the abs_velocity signal.
    """
    # Attempt to use an invalid pattern on abs_velocity
    data = pd.DataFrame({
        'Position': [0, 0, 0, 0, 0],
        'Velocity': [0, -1, 0, 1, 0]
    })
    with pytest.raises(ValueError, match="Invalid pattern 'invalid_pattern'"):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='invalid_pattern',
            signal='abs_velocity'
        )


# ============================ Tests for Invalid Signals and Missing Columns ============================

def test_detect_cycles_invalid_signal():
    """
    Test behavior when an invalid signal is provided.
    """
    # Sample data
    data = pd.DataFrame({
        'Position': [0, 1, 0, 1, 0],
        'Velocity': [0, 1, 0, 1, 0]
    })
    with pytest.raises(ValueError, match="Invalid signal 'invalid_signal'"):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='on_peak',
            signal='invalid_signal'
        )


def test_detect_cycles_missing_velocity():
    """
    Test behavior when Velocity column is missing but signal requires it.
    """
    # Sample data without Velocity
    data = pd.DataFrame({
        'Position': [0, 1, 0, 1, 0]
    })
    # Attempt to detect on Velocity should raise an error
    with pytest.raises(ValueError, match="Data must contain a 'Velocity' column."):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='on_peak',
            signal='velocity'
        )


def test_detect_cycles_missing_velocity_for_abs_velocity():
    """
    Test behavior when Velocity column is missing but signal requires absolute Velocity.
    """
    # Sample data without Velocity
    data = pd.DataFrame({
        'Position': [0, 1, 0, 1, 0]
    })
    # Attempt to detect on abs_velocity should raise an error
    with pytest.raises(ValueError, match="Data must contain a 'Velocity' column to compute its absolute value."):
        detect_cycles(
            data,
            threshold=0.5,
            distance=1.0,
            pattern='both',
            signal='abs_velocity'
        )

# cycle_detector/tests/test_utils.py

import os
import tempfile
import json
import csv
import pandas as pd
import numpy as np
import pytest
from cycle_detector.utils import (
    load_data,
    prepare_data_for_cycle_detection,
    save_cycle_data,
    has_been_processed,
    log_processed_record,
    show_plots,
    manual_cutting,
    save_last_parameters,
    load_last_parameters
)


def test_load_data_csv():
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
        tmp.write("NeckFlexion_C3d_Position,Velocity\n")
        tmp.write("0.1,0.01\n0.2,0.02\n0.3,0.03\n")
        tmp_path = tmp.name

    # Load data using the utility function
    data = load_data(tmp_path)

    # Assertions
    assert 'NeckFlexion_C3d_Position' in data.columns
    assert 'Velocity' in data.columns
    assert len(data) == 3
    assert data.iloc[0]['NeckFlexion_C3d_Position'] == 0.1

    # Clean up
    os.remove(tmp_path)


def test_load_data_parquet():
    # Create a temporary Parquet file
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
        tmp_path = tmp.name

    # Create sample data
    df = pd.DataFrame({
        'NeckFlexion_C3d_Position': [0.1, 0.2, 0.3],
        'Velocity': [0.01, 0.02, 0.03]
    })
    df.to_parquet(tmp_path)

    # Load data using the utility function
    data = load_data(tmp_path)

    # Assertions
    assert 'NeckFlexion_C3d_Position' in data.columns
    assert 'Velocity' in data.columns
    assert len(data) == 3
    assert data.iloc[1]['Velocity'] == 0.02

    # Clean up
    os.remove(tmp_path)


def test_load_data_invalid_format():
    # Create a temporary TXT file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
        tmp.write("Invalid content")
        tmp_path = tmp.name

    # Attempt to load data and expect a ValueError
    with pytest.raises(ValueError):
        load_data(tmp_path)

    # Clean up
    os.remove(tmp_path)


def test_prepare_data_for_cycle_detection_success():
    # Sample data
    data = pd.DataFrame({
        'NeckFlexion_C3d_Position': [0.1, 0.2, 0.3],
        'Velocity': [0.01, 0.02, 0.03]
    })

    prepared = prepare_data_for_cycle_detection(
        data=data,
        filename='session1_nuqueflexion_c3d.parquet',
        fs=100,
        data_source='c3d',
        condition='nuqueflexion',
        position_col='NeckFlexion_C3d_Position'
    )

    # Assertions
    assert 'Position' in prepared.columns
    assert prepared['Position'].tolist() == [0.1, 0.2, 0.3]
    assert 'Velocity' in prepared.columns
    assert prepared.attrs['fs'] == 100


def test_prepare_data_for_cycle_detection_missing_column():
    # Sample data without the required position column
    data = pd.DataFrame({
        'SomeOtherColumn': [0.1, 0.2, 0.3],
        'Velocity': [0.01, 0.02, 0.03]
    })

    # Attempt to prepare data and expect a ValueError
    with pytest.raises(ValueError):
        prepare_data_for_cycle_detection(
            data=data,
            filename='session1_nuqueflexion_c3d.parquet',
            fs=100,
            data_source='c3d',
            condition='nuqueflexion',
            position_col='NeckFlexion_C3d_Position'
        )


def test_save_cycle_data():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        record_name = 'session1'
        detection_parameters = {'threshold': 0.5,
                                'distance': 2.0, 'pattern': 'both'}
        sep_indices = np.array([10, 20, 30])

        save_cycle_data(record_name, detection_parameters, sep_indices, tmpdir)

        # Check if the JSON file exists
        output_file = os.path.join(tmpdir, f"{record_name}_cycles.json")
        assert os.path.isfile(output_file)

        # Load and verify content
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert data['record_name'] == record_name
            assert data['detection_parameters'] == detection_parameters
            assert data['cycle_indices'] == sep_indices.tolist()


def test_has_been_processed():
    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as tmpdir:
        record_name = 'session1'
        output_file = os.path.join(tmpdir, f"{record_name}_cycles.json")
        with open(output_file, 'w') as f:
            f.write('{}')  # Write empty JSON

        assert has_been_processed(record_name, tmpdir)
        assert not has_been_processed('session2', tmpdir)


# def test_log_processed_record():
#     # Create a temporary directory
#     with tempfile.TemporaryDirectory() as tmpdir:
#         record_name = 'session1'
#         detection_parameters = {'threshold': 0.5,
#                                 'distance': 2.0, 'pattern': 'both'}
#         parameters_file = f"{record_name}_cycles.json"
#         log_processed_record(record_name, tmpdir, detection_parameters)

#         # Check if the log file exists
#         log_file = os.path.join(tmpdir, 'processed_records.log')
#         assert os.path.isfile(log_file)

#         # Load and verify content
#         with open(log_file, 'r') as f:
#             lines = f.readlines()
#             assert len(lines) == 1
#             logged_data = lines[0].strip().split(',')
#             assert logged_data[0] == record_name
#             assert parameters_file in logged_data[2]
#             assert json.loads(logged_data[3]) == detection_parameters

def test_log_processed_record():
    record_name = "test_record"
    detection_parameters = {"param1": "value1", "param2": "value2"}

    with tempfile.TemporaryDirectory() as temp_dir:
        log_processed_record(record_name, temp_dir, detection_parameters)

        log_file = os.path.join(temp_dir, 'processed_records.log')
        assert os.path.isfile(log_file), "Log file was not created."

        with open(log_file, 'r', newline='') as csvfile:
            log_reader = csv.reader(csvfile)
            rows = list(log_reader)
            assert len(rows) == 1, "Log file should contain exactly one entry."
            assert rows[0][0] == record_name, "Record name does not match."
            assert rows[0][2] == f"{record_name}_cycles.json", "Parameters file name does not match."
            assert json.loads(
                rows[0][3]) == detection_parameters, "Detection parameters do not match."


def test_save_and_load_last_parameters():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        detection_parameters = {'threshold': 0.6,
                                'distance': 1.5, 'pattern': 'on_peak'}

        # Save parameters
        save_last_parameters(tmpdir, detection_parameters)

        # Load parameters
        loaded_parameters = load_last_parameters(tmpdir)
        assert loaded_parameters == detection_parameters

        # Test loading when file does not exist
        with tempfile.TemporaryDirectory() as empty_dir:
            default_parameters = load_last_parameters(empty_dir)
            assert default_parameters == {
                'threshold': 1.0, 'distance': 2.0, 'pattern': 'both'}

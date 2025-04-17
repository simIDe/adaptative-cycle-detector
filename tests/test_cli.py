# cycle_detector/tests/test_cli.py

import os
import tempfile
import json
import pytest
import pandas as pd
from click.testing import CliRunner
from cycle_detector.cli import main
from cycle_detector.utils import load_data


@pytest.fixture
def runner():
    return CliRunner()


def create_sample_data_csv(tmpdir, position_col='NeckFlexion', velocity_col='Velocity'):
    data = pd.DataFrame({
        position_col: [0.1, 0.2, 0.7, 1.2, 0.5, 0.4, 0.3, 0.2, 1.1, 0.8, 0.3, 0.5, 0.2, 0.1],
        velocity_col: [0.01, 0.02, 0.03, 0.04, 0.05, 0.04,
                       0.03, 0.02, 0.01, 0.02, 0.03, 0.05, 0.02, 0.01]
    })
    file_path = os.path.join(tmpdir, 'session1_nuqueflexion_c3d.csv')
    data.to_csv(file_path, index=False)
    return file_path


def test_cli_no_matching_files(runner):
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(main, [
            '--data-path', tmpdir,
            '--output-dir', tmpdir,
            '--fs', '100',
            '--pattern', 'both',
            '--data-source', 'c3d',
            '--condition', 'nuqueflexion',
            '--position-col', 'NeckFlexion'
        ])
        assert result.exit_code == 0
        assert "No CSV or Parquet records found matching the specified data source and condition." in result.output


def test_cli_successful_processing(runner):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample CSV data
        file_path = create_sample_data_csv(tmpdir)

        # Invoke CLI
        result = runner.invoke(main, [
            '--data-path', tmpdir,
            '--output-dir', tmpdir,
            '--fs', '100',
            '--pattern', 'both',
            '--data-source', 'c3d',
            '--condition', 'nuqueflexion',
            '--position-col', 'NeckFlexion'
        ], input='Y\n')  # Simulate user input 'Y' to accept detection results

        # Assertions
        assert result.exit_code == 0
        assert "Processing record: session1_nuqueflexion_c3d" in result.output
        assert "Saved cycle data to" in result.output
        assert "Processing completed for all records." in result.output

        # Verify output JSON
        output_json = os.path.join(
            tmpdir, 'session1_nuqueflexion_c3d_cycles.json')
        assert os.path.isfile(output_json)
        with open(output_json, 'r') as f:
            data = json.load(f)
            assert data['record_name'] == 'session1_nuqueflexion_c3d'
            assert data['detection_parameters']['pattern'] == 'both'
            assert isinstance(data['cycle_indices'], list)


def test_cli_already_processed(runner):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample CSV data
        file_path = create_sample_data_csv(tmpdir)

        # Create an existing cycle JSON to simulate already processed
        existing_json = os.path.join(
            tmpdir, 'session1_nuqueflexion_c3d_cycles.json')
        with open(existing_json, 'w') as f:
            json.dump({}, f)

        # Invoke CLI and choose not to reprocess
        result = runner.invoke(main, [
            '--data-path', tmpdir,
            '--output-dir', tmpdir,
            '--fs', '100',
            '--pattern', 'both',
            '--data-source', 'c3d',
            '--condition', 'nuqueflexion',
            '--position-col', 'NeckFlexion'
        ], input='N\n')  # Simulate user input 'N' to skip reprocessing

        # Assertions
        assert result.exit_code == 0
        assert "Record 'session1_nuqueflexion_c3d' has already been processed." in result.output
        assert "Processing completed for all records." in result.output


def test_cli_invalid_position_col(runner):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample CSV data with different position column
        data = pd.DataFrame({
            'DifferentPositionCol': [0.1, 0.2, 0.3],
            'Velocity': [0.01, 0.02, 0.03]
        })
        file_path = os.path.join(tmpdir, 'session1_nuqueflexion_c3d.csv')
        data.to_csv(file_path, index=False)

        # Invoke CLI with incorrect position column
        result = runner.invoke(main, [
            '--data-path', tmpdir,
            '--output-dir', tmpdir,
            '--fs', '100',
            '--pattern', 'both',
            '--data-source', 'c3d',
            '--condition', 'nuqueflexion',
            '--position-col', 'NeckFlexion'  # Incorrect column
        ])

        # Assertions
        # assert result.exit_code != 0
        assert "Position column 'NeckFlexion' not found in data." in result.output


def test_cli_manual_cutting(runner, monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample CSV data
        file_path = create_sample_data_csv(tmpdir)

        # Mock ginput to simulate manual cutting (e.g., user clicks at positions 2 and 4)
        # We'll need to mock matplotlib's ginput function
        def mock_ginput(n=-1, timeout=0):
            return [(2, 0), (4, 0)]  # Simulated user clicks

        monkeypatch.setattr('matplotlib.pyplot.ginput', mock_ginput)

        # Invoke CLI and simulate user inputs
        # First 'N' to reject initial detection, then 'Y' to accept manual cuts
        result = runner.invoke(main, [
            '--data-path', tmpdir,
            '--output-dir', tmpdir,
            '--fs', '100',
            '--pattern', 'both',
            '--data-source', 'c3d',
            '--condition', 'nuqueflexion',
            '--position-col', 'NeckFlexion'
        ], input='N\n0\n0\non_peak\nY\n')  # Simulate rejecting initial detection and accepting manual cuts

        # Assertions
        assert result.exit_code == 0
        assert "Rendering the manual cuts for validation..." in result.output
        assert "Saved cycle data to" in result.output

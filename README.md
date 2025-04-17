# Adaptive Cycle Detection Tool

The **Adaptive Cycle Detection Tool** is a versatile command-line application designed to detect and analyze cycles within experimental data. Whether you're working with biomechanics, signal processing, or any field requiring cycle analysis, this tool provides a streamlined and customizable approach to identifying cycle boundaries based on your specific data sources and experimental conditions.

---

## Table of Contents

- [Adaptive Cycle Detection Tool](#adaptive-cycle-detection-tool)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command-Line Options](#command-line-options)
    - [Example Commands](#example-commands)
  - [Processing Workflow](#processing-workflow)
  - [Output](#output)
  - [Dependencies](#dependencies)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)
  - [Acknowledgments](#acknowledgments)

---

## Features

- **Flexible File Filtering:** Process only the files that match specific data sources and experimental conditions.
- **Customizable Column Selection:** Directly specify the position column used for cycle detection.
- **Multiple Detection Patterns:** Choose between detecting peaks, troughs, or both for identifying cycle boundaries.
- **Manual Cycle Cutting:** Interactive feature allowing users to manually define cycle boundaries with validation.
- **Parameter Persistence:** Saves and loads the last used detection parameters for consistent analysis across sessions.
- **Comprehensive Logging:** Keeps track of processed records with timestamps and detection parameters.
- **Supports Multiple File Formats:** Handles both CSV and Parquet data files.

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/cycle_detector.git
   cd cycle_detector
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   Ensure you have [Python 3.6+](https://www.python.org/downloads/) installed.

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

The **Adaptive Cycle Detection Tool** is operated via the command line. Below are the available options and examples to help you get started.

### Command-Line Options

| Option           | Shortcut | Description                                                 | Required | Default  |
| ---------------- | -------- | ----------------------------------------------------------- | -------- | -------- |
| `--data-path`    | `-d`     | Path to the directory containing your data files.           | Yes      | N/A      |
| `--output-dir`   | `-o`     | Directory to save cycle detection results and logs.         | No       | `output` |
| `--fs`           | `-f`     | Sampling frequency of your data in Hz.                      | Yes      | N/A      |
| `--pattern`      | `-p`     | Detection pattern: `on_peak`, `between_peak`, or `both`.    | No       | `both`   |
| `--data-source`  | `-s`     | Keyword to filter files based on data source (e.g., `c3d`). | Yes      | N/A      |
| `--condition`    | `-c`     | Keyword to filter files based on experimental condition.    | Yes      | N/A      |
| `--position-col` | `-P`     | Name of the position column in your data file.              | Yes      | N/A      |
| `--help`         | `-h`     | Show the help message and exit.                             | No       | N/A      |

### Example Commands

1. **Basic Usage**

   Process all files in the `./data` directory that contain the keywords `c3d` (data source) and `neckflexion` (condition), using `neckflexion_pos` as the position column.

   ```bash
   python cycle_detector/cli.py \
     --data-path ./data \
     --output-dir ./cycle_detection_output \
     --fs 100 \
     --pattern both \
     --data-source c3d \
     --condition neckflexion \
     --position-col neckflexion_pos
   ```

2. **Using Shortcuts**

   The tool supports shortcuts for quicker command entry.

   ```bash
   python cycle_detector/cli.py \
     -d ./data \
     -o ./results \
     -f 100 \
     -p on_peak \
     -s xsens \
     -c tronflexion \
     -P TrunkFlexion_Xsens_Position
   ```

3. **Displaying Help**

   To view all available options and their descriptions:

   ```bash
   python cycle_detector/cli.py --help
   ```

   or using the shortcut:

   ```bash
   python cycle_detector/cli.py -h
   ```

---

## Processing Workflow

1. **File Filtering**

   The tool scans the specified `--data-path` directory for `.csv` and `.parquet` files that match both the `--data-source` and `--condition` keywords in their filenames.

2. **Data Loading and Preparation**

   For each matching file:

   - Loads the data from the specified `--position-col`.
   - Optionally includes the corresponding velocity column if it exists (assumes a naming convention where 'Velocity' replaces 'Position' in the column name).
   - Stores the sampling frequency (`--fs`) as an attribute for use in detection.

3. **Cycle Detection**

   - Detects cycle boundaries based on the selected `--pattern`:
     - `on_peak`: Detects peaks above a threshold.
     - `between_peak`: Detects troughs below a threshold.
     - `both`: Detects both peaks and troughs.
   - Renders plots for visual verification.

4. **Interactive Parameter Adjustment**

   - If the detection results are unsatisfactory, users can adjust detection parameters:
     - **Threshold**: The value above or below which peaks or troughs are detected.
     - **Distance**: The minimum distance between consecutive peaks/troughs in seconds.
     - **Pattern**: The detection pattern as described above.
   - Optionally, users can perform manual cutting to define cycle boundaries by interacting with the rendered plots.

5. **Manual Cutting and Validation**

   - Users can manually select cycle boundaries by clicking on the plot.
   - After selection, the tool renders the cuts and prompts the user to accept or restart the manual cutting process.

6. **Saving Results**

   - Detection results, including cycle indices and detection parameters, are saved in a structured JSON file within the `--output-dir`.
   - Processed records are logged with timestamps and parameter details.
   - The last used detection parameters are saved for consistency in subsequent runs.

---

## Output

- **Cycle Detection Results**

  For each processed file, a JSON file named `<record_name>_cycles.json` is created in the `--output-dir`. This file contains:

  - `record_name`: Name of the processed record.
  - `detection_parameters`: Parameters used for cycle detection.
  - `cycle_indices`: List of detected cycle boundary indices.
  - `timestamp`: ISO-formatted timestamp of processing.

- **Processed Records Log**

  A log file named `processed_records.log` is maintained in the `--output-dir`, recording:

  - `record_name`: Name of the processed record.
  - `timestamp`: ISO-formatted timestamp of processing.
  - `parameters_file`: Reference to the JSON file containing detection results.
  - `detection_parameters`: Parameters used for detection.

- **Last Used Parameters**

  A file named `last_parameters.json` in the `--output-dir` stores the last used detection parameters, which are loaded as defaults in subsequent runs.

---

## Dependencies

Ensure you have [Python 3.6+](https://www.python.org/downloads/) installed. The tool relies on the following Python packages:

- [Click](https://click.palletsprojects.com/): For building the command-line interface.
- [Pandas](https://pandas.pydata.org/): For data manipulation and analysis.
- [NumPy](https://numpy.org/): For numerical operations.
- [Matplotlib](https://matplotlib.org/): For plotting and visualization.
- [SciPy](https://www.scipy.org/): For signal processing and cycle detection.
- [PyArrow](https://arrow.apache.org/docs/python/): For handling Parquet files.

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

## Contributing

Contributions are welcome! Whether you're fixing bugs, improving documentation, or adding new features, your efforts are appreciated.

1. **Fork the Repository**

2. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make Your Changes**

4. **Commit Your Changes**

   ```bash
   git commit -m "Add your descriptive commit message here"
   ```

5. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Submit a Pull Request**

   Describe your changes and the problem they solve. Include screenshots if applicable.

---

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE). You can freely use, modify, and distribute this software under the terms of the license.

---

## Contact

For any questions, suggestions, or feedback, please reach out:

- **Email:** simon.bastide@outlook.com
- **GitHub:** [@simIDe](https://github.com/simIDe)
- **LinkedIn:** [Simon Bastide](https://www.linkedin.com/in/simonbastide/)

---

## Acknowledgments

- Inspired by the need for flexible and user-friendly cycle detection in experimental data.
- Thanks to the open-source community for providing invaluable tools and libraries.

---

*Happy Cycling Detection! 🚴‍♂️*

---
# Installation Guide - Quantum Gravity Discovery Dataset

## System Requirements

- **Operating System:** Windows 10+, macOS 10.14+, or Linux
- **Python:** Version 3.8 or higher
- **Memory:** Minimum 4GB RAM (8GB recommended)
- **Storage:** Minimum 2GB free space
- **Internet:** Required for data downloads

## Python Installation

### Windows:
1. Download Python from https://python.org
2. Install with "Add Python to PATH" checked
3. Open Command Prompt and verify: `python --version`

### macOS:
```bash
brew install python3
```

### Linux:
```bash
sudo apt-get install python3 python3-pip
```

## Required Packages

Install required packages using pip:

```bash
pip install numpy matplotlib scipy astropy pandas requests
```

Or install from requirements file:
```bash
pip install -r requirements.txt
```

## Dataset Installation

1. **Download Dataset:**
   - Download from Zenodo
   - Extract to desired location

2. **Verify Installation:**
   ```bash
   cd quantum-gravity-discovery-v1.0.0
   python code/test.py
   ```

## Usage Examples

### Basic Analysis:
```python
from code.test import analyze_qg_signal, load_grb_data

# Load GRB data
grb_data = load_grb_data('data/real_astronomical_data/fermi/grb080916c_realistic.fits')

# Analyze quantum gravity signal
result = analyze_qg_signal(grb_data)
print(f"E_QG: {result['fit_results']['E_QG_GeV']:.2e} GeV")
```

### Generate Scientific Paper:
```python
python code/scientific_paper_generator.py
```

### Run Forensic Investigation:
```python
python code/forensic_investigation.py
```

## Troubleshooting

### Common Issues:

1. **ImportError:** Install missing packages
2. **FileNotFoundError:** Check file paths
3. **Memory Error:** Reduce dataset size or increase RAM

### Support:
- Email: info@rthitalia.com
- Documentation: See README.md

## Version History

- **v1.0.0** - Initial release with discovery data and analysis tools

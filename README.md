# pypeline

A Python package for cosmological data analysis pipeline, specializing in thermal Sunyaev-Zeldovich (tSZ) effect analysis, cluster catalogues, and statistical inference from CMB maps.

## Overview

`pypeline` provides a comprehensive suite of tools for processing and analyzing cosmological data, with a focus on:

- **Cluster catalogue generation** from cosmological parameters
- **Coordinate attribution and sampling** for sky patches
- **tSZ signal painting** using XGPaint integration
- **Empirical power spectrum computation** from FITS maps
- **Theoretical calculations** for power spectra and covariances
- **Wavelet Scattering Transform (WST) analysis** for non-Gaussian features
- **Statistical inference** via covariance matrices and correlations
- **Patch synthesis** from statistical summaries

## Installation

### From source

```bash
git clone <repository-url>
cd pypeline
pip install -e .
```

### Dependencies

Core dependencies (automatically installed):
- `numpy` - Array operations
- `scipy` - Scientific computing
- `matplotlib` - Visualization

Additional dependencies for full functionality:
- `astropy` - FITS file handling
- `healpy` - HEALPix operations
- `pandas` - Data management
- `tszpower` - Theoretical tSZ power spectrum calculations
- `scattering` - Wavelet scattering transforms
- Julia with `XGPaint.jl` - For patch painting

### Development

```bash
pip install -e ".[dev]"
```

This installs additional tools: `pytest`, `black`, `flake8`, `mypy`

## Quick Start

### 1. Generate Cosmological Parameter Grid

```python
from pypeline import make_lhs_and_convert

# Create Latin Hypercube sample of cosmological parameters
df = make_lhs_and_convert(
    N=5,
    sigma8_interval=(0.7, 0.9),
    omegam_interval=(0.25, 0.35),
    seed=42,
    returned_params=["Oc0h2", "logA"]
)

df.to_csv("cosmological_parameters.csv", index=False)
```

### 2. Attribute Coordinates to Catalogues

```python
from pypeline import process_catalogues

process_catalogues(
    input_dir="path/to/catalogues",
    ra0_deg=0, dec0_deg=0,
    w_deg=10, h_deg=10,
    seed=42,
    recursive=True,
    lon_wrap="pm_pi"
)
```

### 3. Paint tSZ Patches

```python
from pypeline import paint_patches

outputs = paint_patches(
    patch_size_deg=10.0,
    pix_res_arcmin=0.5,
    output_dir="output/patches",
    catalogs=["path/to/catalogues"],
    nx=128,
    xgpaint_url="path/to/XGPaint.jl"
)
```

### 4. Compute Empirical Power Spectrum

```python
from pypeline import compute_dell_empiriques

results = compute_dell_empiriques(
    "path/to/fits/directory",
    plot=True,
    area_weighted=False,
    save_csv="output/power_spectrum.csv",
    save_plot="output/power_spectrum.png"
)
```

### 5. Compute Theoretical Power Spectrum

```python
from pypeline import compute_tsz_power_with_errors_from_title_or_csv

ell, D_ell, err_full, err_gauss, allpars = compute_tsz_power_with_errors_from_title_or_csv(
    "path/to/cosmology",
    show_plot=True,
    use_full_error=True,
    f_sky=1.9e-03
)
```

### 6. Wavelet Scattering Transform Analysis

```python
from pypeline import compute_wst_S012

results = compute_wst_S012(
    "path/to/fits/directory",
    J=7, L=4,
    device="auto",
    whiten=False,
    samples_format='long',
    plot=True,
    which="S1",
    save_samples_csv="output/wst/",
    save_plot="output/wst_plots/"
)
```

### 7. Compute Covariance Matrix

```python
from pypeline import compute_covariance_mixed

results = compute_covariance_mixed(
    wst_inputs="path/to/wst_samples.csv",
    dell_inputs="path/to/power_spectrum.csv",
    align="truncate",
    save_npz="output/covariance.npz",
    plot=True
)

cov_matrix = results["cov"]
```

### 8. Generate Patches from Statistics

```python
from pypeline import generate_patch_from_csv

# From power spectrum
patch = generate_patch_from_csv(
    method='spectrum',
    patch_size=(300, 300),
    pixel_scale_arcmin=0.5,
    csv_path='path/to/power_spectrum.csv',
    seed=42,
    output_path='output/patch_from_spectrum.npy'
)

# From WST coefficients
patch_wst = generate_patch_from_csv(
    method='wst',
    patch_size=(300, 300),
    pixel_scale_arcmin=0.5,
    csv_path='path/to/wst_samples.csv',
    seed=42,
    device='cpu',
    output_path='output/patch_from_wst.npy',
    synthesis_kwargs={
        "estimator_name": "wst",
        "mode": "estimator",
        "J": 7, "L": 4,
        "steps": 400,
        "learning_rate": 0.4
    }
)
```

## Module Overview

### Core Modules

#### `coordinates_attributor_en`
Coordinate system utilities and sampling:
- `wrap_pm_pi()` - Wrap angles to [-π, π]
- `sample_lonlat_patch()` - Sample positions in a sky patch
- `process_catalogues()` - Batch process cluster catalogues

#### `correlation`
Statistical correlation tools:
- `covariance_to_correlation()` - Convert covariance to correlation matrix

#### `cov_en`
Covariance computation:
- `load_s1_samples_from_path()` - Load WST S1 samples
- `load_s0s1_samples_from_csv()` - Load S0/S1 samples
- `compute_covariance_mixed()` - Compute mixed covariance matrices

#### `emp_ps_en`
Empirical power spectrum from FITS maps:
- `compute_dell_empiriques()` - Compute D_ell with error bars

#### `generators`
Patch generation from statistical summaries:
- `generate_patch_from_csv()` - Generate patches from power spectrum or WST
- `example_notebook_usage()` - Example usage patterns

#### `grid_creator_ve`
Cosmological parameter grid generation:
- `FixedCosmo` - Fixed cosmology class
- `make_lhs_and_convert()` - Latin Hypercube Sampling for parameter grids

#### `patch_painter_ve`
tSZ patch painting:
- `paint_patches()` - Paint tSZ signals on sky patches using XGPaint

#### `theoretical_cov`
Theoretical covariance computation:
- `compute_theoretical_covariance_from_source()` - Compute theoretical covariances
- `compute_theoretical_covariance_from_title()` - Backward compatibility wrapper

#### `theoretical_power_spec`
Theoretical power spectrum:
- `compute_tsz_power_with_errors_from_title_or_csv()` - Compute tSZ power spectra with uncertainties

#### `wst_en`
Wavelet Scattering Transform analysis:
- `read_fits_image()` - Read FITS images
- `load_images_from_path()` - Batch load FITS images
- `compute_wst_S012()` - Compute WST coefficients (S0, S1, S2)

## Examples

### Example Notebooks

1. **`example_notebook.ipynb`** - Complete pipeline demonstration from parameter generation to statistical analysis
2. **`tutorial_power_spectrum.ipynb`** - Power spectrum computation tutorial

## Use Cases

### Cosmological Parameter Inference
Use the pipeline to:
1. Generate parameter grids with LHS sampling
2. Create mock cluster catalogues
3. Paint tSZ patches
4. Compute empirical and theoretical statistics
5. Compare observations with predictions

### Statistical Analysis
- Extract power spectra and WST coefficients from CMB maps
- Compute covariance matrices for joint analyses
- Generate synthetic data matching observed statistics

### tSZ Science
- Model tSZ signals from cluster catalogues
- Compare empirical vs theoretical power spectra
- Study non-Gaussian features with WST

## Pipeline Workflow

```
Cosmological Parameters (CSV/DataFrame)
    ↓
Generate Cluster Catalogues
    ↓
Assign Coordinates to Patches
    ↓
Paint tSZ Signals (XGPaint)
    ↓
Compute Statistics ←→ Theoretical Predictions
    ├─ Power Spectrum      ├─ Theory Power Spectrum
    ├─ WST Coefficients    └─ Theory Covariance
    └─ Covariances
    ↓
Inference / Patch Synthesis
```

## Requirements

- Python >= 3.8
- For full functionality: Julia with XGPaint.jl
- External dependencies: `tszpower`, `scattering` transform package

## Development Status

- **Status**: Alpha (v0.1.0)
- **License**: MIT
- **Python Support**: 3.8, 3.9, 3.10, 3.11

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black pypeline/`
6. Submit a pull request

## Citation

If you use this package in your research, please cite:
```
[Add citation information when available]
```

## Support

For issues, questions, or contributions:
- Open an issue on the repository
- Check the example notebooks for usage patterns
- Review the docstrings in each module

## References

- tSZ effect and cluster physics
- Wavelet Scattering Transforms for cosmology
- Latin Hypercube Sampling for parameter exploration
- XGPaint for realistic tSZ signal painting

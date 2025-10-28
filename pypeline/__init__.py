"""
pypeline - A Python package for cosmological data analysis pipeline

This package provides tools for:
- Coordinate attribution and sampling
- Empirical power spectrum computation
- Covariance matrix computation
- WST (Wavelet Scattering Transform) analysis
- Theoretical power spectrum and covariance calculations
- Parameter grid generation
- Patch painting with tSZ signals
- Statistical correlation analysis
- Data generation from CSV files
"""

__version__ = "0.1.0"

# Core coordinate and sampling utilities
from .coordinates_attributor_en import (
    wrap_pm_pi,
    sample_lonlat_patch,
    process_catalogues
)

# Statistical correlation tools
from .correlation import covariance_to_correlation

# Covariance computation utilities
from .cov_en import (
    load_s1_samples_from_path,
    load_s0s1_samples_from_csv,
    compute_covariance_mixed
)

# Empirical power spectrum computation
from .emp_ps_en import (
    compute_dell_empirical
)

# Data generation from CSV files
from .generators import (
    generate_patch_from_csv,
    example_notebook_usage
)

# Parameter grid generation
from .grid_creator_ve import (
    FixedCosmo,
    make_lhs_and_convert
)

# tSZ patch painting
from .patch_painter_ve import (
    paint_patches
)

# Theoretical covariance computation
from .theoretical_cov import (
    compute_theoretical_covariance_from_source,
    compute_theoretical_covariance_from_title  # backward compatibility
)

# Theoretical power spectrum computation
from .theoretical_power_spec import (
    compute_tsz_power_with_errors_from_title_or_csv
)

# WST analysis tools
from .wst_en import (
    read_fits_image,
    load_images_from_path,
    compute_wst_S012
)

__all__ = [
    # Coordinate utilities
    'wrap_pm_pi',
    'sample_lonlat_patch',
    'process_catalogues',
    
    # Correlation analysis
    'covariance_to_correlation',
    
    # Covariance computation
    'load_s1_samples_from_path',
    'load_s0s1_samples_from_csv',
    'compute_covariance_mixed',
    
    # Empirical power spectrum
    'compute_dell_empirical',
    
    # Data generation
    'generate_patch_from_csv',
    'example_notebook_usage',
    
    # Parameter grid generation
    'FixedCosmo',
    'make_lhs_and_convert',
    
    # tSZ patch painting
    'paint_patches',
    
    # Theoretical calculations
    'compute_theoretical_covariance_from_source',
    'compute_theoretical_covariance_from_title',
    'compute_tsz_power_with_errors_from_title_or_csv',
    
    # WST analysis
    'read_fits_image',
    'load_images_from_path',
    'compute_wst_S012'
]
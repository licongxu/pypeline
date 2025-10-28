from typing import Tuple, Optional, Any, Dict
from copy import deepcopy
import os, csv
import numpy as np
import matplotlib.pyplot as plt

# --- Parsing via extract_params  ---
# from title_reader import extract_params

# --- Default base values  ---
DEFAULT_ALLPARS: Dict[str, float | int] = {
    'omega_b': 0.02242,
    'omega_cdm': 0.1193,
    'H0': 67.66,
    'tau_reio': 0.0544,
    'ln10^{10}A_s': 2.972,
    'n_s': 0.9665,
    'M_min': 1.0e14 * 0.6766,
    'M_max': 1.0e16 * 0.6766,
    'z_min': 1e-2,
    'z_max': 3.0,
    'P0GNFW': 8.130,
    'c500': 1.156,
    'gammaGNFW': 0.3292,
    'alphaGNFW': 1.0620,
    'betaGNFW': 5.4807,
    'B': 1.41,
    "cosmo_model": 0,     # 1: mnu-lcdm emulators; 0: lcdm neutrino mass fixed
    'jax': 1,
}

# Mapping CSV/params -> tszpower keys
_KEY_MAP = {
    'Ob0h2': 'omega_b',
    'Oc0h2': 'omega_cdm',
    'n_s': 'n_s',
    'logA': 'ln10^{10}A_s',
    'B': 'B',
}

def _parse_params_from_csv(csv_path: str) -> Dict[str, float]:
    """Read the first row of a CSV and return a dict of parameters."""
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        row = next(reader)
    out = {}
    for k, v in row.items():
        if v is None or v == "":
            continue
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v
    return out

def _build_allpars_from_params(
    params: Dict[str, float],
    base: Optional[Dict[str, float | int]] = None,
    include_extras: bool = True
) -> Dict[str, float | int]:
    """Build allpars directly from a dict of parameters (from CSV or title)."""
    allpars = deepcopy(DEFAULT_ALLPARS if base is None else base)

    # h -> H0 and rescale masses
    h = params.get('h', None)
    if h is not None:
        try:
            h = float(h)
            allpars['H0'] = 100.0 * h
            # force masses consistent with h
            allpars['M_min'] = 1.0e14 * h
            allpars['M_max'] = 1.0e16 * h
        except (TypeError, ValueError):
            pass

    # direct mapping of keys to what tszpower expects
    for src_key, dst_key in _KEY_MAP.items():
        if src_key in params:
            try:
                allpars[dst_key] = float(params[src_key])
            except (TypeError, ValueError):
                pass

    # possible extras
    if include_extras:
        for extra in ('A_cib', 'A_ir', 'A_rs'):
            if extra in params:
                try:
                    allpars[extra] = float(params[extra])
                except (TypeError, ValueError):
                    pass
    return allpars

def _normalise_params_from_source(source: str) -> Dict[str, float]:
    """
    Return a flat dict of parameters from a CSV or a *title* parsed by extract_params.
    Handle the case where extract_params returns {file: {...}}.
    """
    if os.path.isfile(source) and source.lower().endswith(".csv"):
        params = _parse_params_from_csv(source)
    else:
        params = extract_params(source)
        # PATCH: if extract_params returns {path: {...}} choose the appropriate entry
        if isinstance(params, dict) and params:
            first_val = next(iter(params.values()))
            if isinstance(first_val, dict):
                if os.path.isfile(source) and source in params:
                    params = params[source]
                else:
                    params = first_val
    # Clean keys (BOM, spaces)
    params = {str(k).strip().lstrip('\ufeff'): v for k, v in params.items()}
    return params

def compute_theoretical_covariance_from_source(
    source: str,
    *,
    initialise_tsz: bool = True,
    use_scaled: bool = True,
    tsz_module: Optional[Any] = None,
    show: bool = True,
    return_fig: bool = True,
    imshow_kwargs: Optional[dict] = None,
    f_sky: float = None
) -> Tuple[np.ndarray, Optional[plt.Figure]]:
    """
    Compute theoretical covariance (trispectrum) from a *title* (via extract_params) or a *CSV*.

    Parameters
    ----------
    source : str
        - Parsable title/name (e.g.: "logA=..._Oc0h2=..._h=...") -> uses extract_params
        - OR path to a CSV file with columns:
          h,n_s,Ob0h2,B,A_cib,A_ir,A_rs,logA,Oc0h2
    initialise_tsz : bool
        If True, does tsz.classy_sz.set(allpars) then tsz.initialise().
    use_scaled : bool
        If True, uses compute_scaled_trispectrum, otherwise compute_trispectrum.
    tsz_module : module
        Optional injection of the tszpower module (useful for tests).
    show : bool
        Display the figure if True.
    return_fig : bool
        Return the Figure if True.
    imshow_kwargs : dict
        Arguments passed to imshow (e.g. {'origin': 'lower'}).

    Returns
    -------
    (cov, fig)
      cov : np.ndarray
      fig : matplotlib.figure.Figure or None
    """
    # 0) Import tszpower here to allow tsz_module injection
    tsz = tsz_module
    if tsz is None:
        import tszpower as tsz

    # 1) Get a flat dict of parameters then build allpars
    params = _normalise_params_from_source(source)
    allpars = _build_allpars_from_params(params)

    # 2) Initialization (set + initialise)
    if initialise_tsz:
        tsz.classy_sz.set(allpars)
        tsz.initialise()
        # Optional: try to compute sigma8 (depending on availability)
        try:
            tsz.classy_sz.get_sigma8_and_der(params_values_dict=allpars)
        except Exception:
            try:
                tsz.classy_sz.get_sigma8_and_der(params_value_dict=allpars)
            except Exception:
                pass

    # 3) Covariance computation via trispectrum
    def _call_with_fallback(fn_scaled: bool):
        if fn_scaled:
            try:
                return tsz.compute_scaled_trispectrum(params_value_dict=allpars)
            except TypeError:
                return tsz.compute_scaled_trispectrum(params_values_dict=allpars)
        else:
            try:
                return tsz.compute_trispectrum(params_value_dict=allpars)
            except TypeError:
                return tsz.compute_trispectrum(params_values_dict=allpars)

    T = _call_with_fallback(use_scaled)
    T = np.asarray(T, dtype=float)

    denom = 4.0 * np.pi * float(f_sky)
    M = T / denom
    cov = M

    # 4) Plot
    fig = None
    if return_fig or show:
        if imshow_kwargs is None:
            imshow_kwargs = {"origin": "lower"}
        else:
            imshow_kwargs = {"origin": "lower", **imshow_kwargs}

        fig, ax = plt.subplots(figsize=(6.5, 5.5))
        im = ax.imshow(cov, **imshow_kwargs)
        ax.set_title("Theoretical covariance (scaled trispectrum)" if use_scaled
                     else "Theoretical covariance (raw trispectrum)")
        ax.set_xlabel(r"$\ell$")
        ax.set_ylabel(r"$\ell'$")
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Amplitude")
        fig.tight_layout()
        if show:
            plt.show()

    return (cov, fig) if return_fig else (cov, None)


# --- Compat: old name (if you want to keep the same API as before) ---
def compute_theoretical_covariance_from_title(*args, **kwargs):
    """Backward compatible wrapper that calls the new function."""
    return compute_theoretical_covariance_from_source(*args, **kwargs)

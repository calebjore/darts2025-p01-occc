import os
import pandas as pd
import numpy as np
from os.path import basename
from batch_config import batch_data_dict

import SintonFMT_LIB as S

__all__ = [
    'jitter_scatter',
    'estimate_pmp_degrad',
    'get_pmp_xaxis',
    'plot_iv_curves_mfr'
]

def jitter_scatter(values, ax, col_num):
    jitter = np.random.uniform(-0.1, 0.1, size=len(values))
    ax.scatter(np.full_like(values, col_num) + jitter, values, alpha=0.6)

def estimate_pmp_degrad(rate, years, nameplate):
    return ((1 - rate) ** years) * nameplate

def get_pmp_xaxis(pmp_pct_col):
    min_pmp_pct = min(pmp_pct_col)
    max_pmp_pct = max(pmp_pct_col)
    xmin = round((min_pmp_pct - 0.05) * 10) / 10
    xmax = round((max_pmp_pct + 0.05) * 10) / 10
    return (xmin, max(xmax, 1)) # ensures max >= 1

def plot_iv_curves_mfr(file, curve_num, ax):
    """
    Plot I–V and pseudo I–V curves from a flash‐test .mfr file.

    Uses S.iv_analysis to extract corrected I–V data at multiple illumination
    levels and then plots the measured I–V (blue dots) and pseudo I–V
    (red dashed dots) for each intensity on the given Axes.

    Parameters
    ----------
    file : str
        Path to the .mfr flash‐test file.
    curve_num : int
        Number of illumination curves to plot (evenly spaced between 0–1 sun,
        excluding the dark I–V).
    ax : matplotlib.axes.Axes
        The matplotlib Axes to draw the scatter plots and annotations on.

    Notes
    -----
    - Requires globally defined ``rsh_v_cell`` and ``step`` variables for
      the IV analysis call.
    - Intensities are sampled via ``np.linspace(0,1,curve_num+1)[1:]`` and rounded.
    - For each target intensity, the nearest actual measured curve is selected.
    - The highest‐intensity curve is annotated “{val} suns”; others just “{val}”.
    """
    corrected_data, mfi_contents = S.iv_analysis(mfr_file=file, reference_constant=None,
                    voltage_temperature_coefficient=None,
                    rsh_v_cell=batch_data_dict['rsh_v_cell'], step=batch_data_dict['step'], sun=None)

    intensity_vals = np.linspace(0, 1, curve_num+1)
    intensity_vals = intensity_vals[1:].round(3) # drop dark-iv
    # print(intensity_vals)

    intensity_array = corrected_data['intensity_array']

    # Plot curve for each val in intensity_vals
    for val in intensity_vals:
        target = val
        closest_val = intensity_array[np.abs(intensity_array - target).argmin()]
        start_idx = int(np.where(intensity_array == closest_val)[0])

        iv_data = corrected_data['iv_curve_intensity'][:,start_idx,:]
        pseudo_iv_data = corrected_data['pseudo-iv_curve_intensity'][:,start_idx,:]

        # Annotate
        if val == intensity_vals.max():
            ax.scatter(pseudo_iv_data[:,0], pseudo_iv_data[:,1], linestyle='--', color='red', s=5, label='pseudo I-V')
            ax.scatter(iv_data[:,0], iv_data[:,1], color='blue', s=5, label='measured I-V')
            ax.text(x=0, y=iv_data[0,1] + 0.1, s=f"{round(closest_val, 3)} suns", fontstyle='italic')
            ax.legend()
        else:
            ax.scatter(pseudo_iv_data[:,0], pseudo_iv_data[:,1], linestyle='--', color='red', s=5)
            ax.scatter(iv_data[:,0], iv_data[:,1], color='blue', s=5)
            ax.text(x=0, y=iv_data[0,1] + 0.1, s=f"{round(closest_val, 3)}", fontstyle='italic')
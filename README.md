# DARTS 2025 – Project 01: OCCC Module Analysis

This repository contains the code used for the OCCC subproject of Project 01 in the UCF DARTS 2025 program. The README will be updated in the future with further information.

Refer to `demo.ipynb` for a demonstrations of the functions in the src files using the data in the occc directory.

<!-- describe what the script does, and what inputs it expects -->
The script expects a directory of Sinton FMT-500 flash test .mfr files, specified by the `iv_dir` parameter in `batch_config.py`.

The script tabulates data in a master dataframe `batch_data`, each row of which contains the serial number of a module, the date and time of a flash test, the irradiance for which key parameters were calculated, and the values of the parameters specified in `batch_config.py`. Further analysis is done by filtering and grouping the master dataframe.

If `batch_config.py` includes a control module, then the script will normalize to those measurements. Otherwise, the script will normalize to the nameplate values.

### Reusing the pipeline

The pipeline can be reused for a different batch of modules. Simply open the batch_config.py file and replace the dictionary values with relevant batch data:
- `identifier`: str, this will be used in visualization titles
- `iv_dir`: str, the directory containing the .mfr files
- `initial_basename_underscore`: bool, the script expects the basename format "IVT20250217-SOLARWORLD_SW-175-MONO-20250217_091818_409049451_X_01", with the first special character a hyphen. If the filename is otherwise identical but includes an underscore rather than a hyphen in this place, set this variable to True so the script can parse it properly.
- `has_basename_comment`: bool, indicates whether the basename includes a comment. In the preceding basename example, this is the "X" before the "01". Set to False if the basenames do not contain a comment field.
- `control`: str, the serial of the control module if present, otherwise set to None
- `modules_to_exclude`: list of str, specify any modules within the directory which you want to exclude from analysis—meaning they won't appear in any visualizations or affect any calculations—or set to None
- `underperforming_serials`: list of str, these modules will be *analyzed* and appear in visualizations, but they will be *excluded* from descriptive statistics. Set to None if you do not wish to exclude modules in this way.
- `cols_to_calc`: list of str, the metrics you want to pull from the .mfr files. Only 'pmp', 'imp', 'vmp', 'isc', 'voc' have been tested across multiple batches, but in theory anything that the S.iv_analysis() function returns a 'intensity_{param}' dict for, meaning any of pmp, imp, vmp, voc, isc, ff, module_efficiency, active_area_efficiency, rs, rsh, pseudo-pmp, pseudo-imp, pseudo-vmp, pseudo-voc, pseudo-isc, pseudo-ff, pseudo-module_efficiency, pseudo-active_area_efficiency.
- `pmp_nameplate`, `vmp_nameplate`, `imp_nameplate`, `voc_nameplate`, `isc_nameplate`: float, nameplate values for these five parameters at standard testing conditions.
- `years`: int, the number of years for which the modules have been installed. Used to calculate degradation rate.
- `suns_to_iter`: list of int, the irradiance values for which to pull parameter measurements. Drastically affects runtime.
- `rsh_v_cell`: used for S.iv_analysis()
- `step`: used for S.iv_analysis()

### Contact
Caleb Jore - ca122980@ucf.edu 

Project Link - https://github.com/calebjore/darts2025-p01-occc/
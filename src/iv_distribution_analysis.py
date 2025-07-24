import os
import pandas as pd
import numpy as np
from os.path import basename
from batch_config import batch_data_dict
import SintonFMT_LIB as S

__all__ = [
    'get_avg_param_per_module',
    'subset_by_intensity',
    'get_control_data_at_intensity',
    'output_summary_stats',
    'norm_to_nameplate',
    'norm_to_control',
    'round_intensity',
    'compute_row',
    'get_serial_file'
]

def get_filename_metadata(file, datatype='iv'):
    '''
    Extracts the metadata from the filename string based on FSEC PVMCF filename
    standards for each measurement type.

    Parameters
    ----------
    file : str
        File path string.
    datatype : str
        Datetype defines which type of measurement you are reading data from.
        Datatype choices: 'iv' 'el' 'dark_iv' 'ir' 'uvf'. The default is 'iv'.

    Returns
    -------
    metadata_dict : dict
        Dictionary of metadata obtained from splitting the filename string.

    '''
    metadata_dict = {}
    bn_split = basename(file).split('_')
    ext = file.split('.')[-1]

    if datatype == 'iv':
        if ext == 'txt':
            metadata_dict['date'] = bn_split[0].split('-')[0]
            metadata_dict['time'] = bn_split[2]
            metadata_dict['make'] = bn_split[0].split('-')[1]
            metadata_dict['model'] = bn_split[1].replace(
                f"-{metadata_dict['date']}", '')
            metadata_dict['serial_number'] = bn_split[3]
            metadata_dict['comment'] = bn_split[4]
            metadata_dict['measurement_number'] = bn_split[5].replace(
                f".{ext}", '')
        else:
            metadata_dict['date'] = bn_split[0].replace(
                'IVT', '').split('-')[0]
            metadata_dict['time'] = bn_split[2]
            metadata_dict['make'] = bn_split[0].split('-')[1]
            metadata_dict['model'] = bn_split[1].replace(
                f"-{metadata_dict['date']}", '')
            metadata_dict['serial_number'] = bn_split[3]
            if batch_data_dict['has_basename_comment']: # custom
                metadata_dict['comment'] = bn_split[4]
                metadata_dict['measurement_number'] = bn_split[5].replace(
                    f".{ext}", '')
            else:
                metadata_dict['measurement_number'] = bn_split[4].replace(
                    f".{ext}", '')
    elif datatype == 'el':
        metadata_dict['date'] = bn_split[0]
        metadata_dict['time'] = bn_split[1]
        metadata_dict['make'] = bn_split[2]
        metadata_dict['model'] = bn_split[3]
        metadata_dict['serial_number'] = bn_split[4]
        metadata_dict['comment'] = bn_split[5]
        metadata_dict['exposure_time'] = bn_split[6].replace('s', '')
        metadata_dict['current'] = bn_split[7].replace('A', '')
        metadata_dict['voltage'] = bn_split[8].replace(f"V.{ext}", '')
    elif datatype == 'ir':
        metadata_dict['date'] = bn_split[0]
        metadata_dict['time'] = bn_split[1]
        metadata_dict['make'] = bn_split[2]
        metadata_dict['model'] = bn_split[3]
        metadata_dict['serial_number'] = bn_split[4]
        metadata_dict['comment'] = bn_split[5]
        metadata_dict['exposure_time'] = bn_split[6].replace('s', '')
        metadata_dict['current'] = bn_split[7].replace(f"A.{ext}", '')
    elif datatype == 'dark_iv':
        metadata_dict['date'] = bn_split[0]
        metadata_dict['time'] = bn_split[1]
        metadata_dict['make'] = bn_split[2]
        metadata_dict['model'] = bn_split[3]
        metadata_dict['serial_number'] = bn_split[4]
        metadata_dict['comment'] = bn_split[5].replace(f".{ext}", '')
    elif datatype == 'uvf':
        metadata_dict['date'] = bn_split[0]
        metadata_dict['time'] = bn_split[1]
        metadata_dict['make'] = bn_split[2]
        metadata_dict['model'] = bn_split[3]
        metadata_dict['serial_number'] = bn_split[4]
        metadata_dict['comment'] = bn_split[5].replace(f".{ext}", '')
    elif datatype == 'v10':
        metadata_dict['serial-number'] = bn_split[4]
        metadata_dict['date'] = bn_split[0]
        metadata_dict['time'] = bn_split[1]
        metadata_dict['delay-time-(s)'] = bn_split[6].split('s')[0]
        metadata_dict['setpoint-total-time-(s)'] = bn_split[5].replace('s', '')
    elif datatype == 'scanner':
        metadata_dict['date'] = bn_split[0]
        metadata_dict['time'] = bn_split[1]
        metadata_dict['module_id'] = bn_split[2]
        metadata_dict['make'] = bn_split[3]
        metadata_dict['model'] = bn_split[4]
        metadata_dict['serial_number'] = bn_split[5]
        metadata_dict['exposure_time'] = bn_split[6]
        metadata_dict['current'] = bn_split[7]
        metadata_dict['voltage'] = bn_split[8]
        metadata_dict['comment'] = bn_split[9].split('.')[0]
        if ext == 'jpg':
            metadata_dict['image_type'] = bn_split[10].split('.')[0]
            if metadata_dict['image_type'] == 'cell':
                metadata_dict['cell_number'] = bn_split[11]

    return metadata_dict

def get_avg_param_per_module(files, dir, sun_list=[1]):
    '''
    Extracts and compiles IV parameters from a list of module files at specified sun levels.

    Parameters
    ----------
    files : list of str
        List of filenames to process.
    dir : str
        Directory path containing the data files.
    sun_list : list of float, optional
        List of sun levels to extract data for. Default is [1].

    Returns
    -------
    parameter_df : pandas.DataFrame
        DataFrame containing metadata and extracted IV parameters for each module.
    '''

    # Define parameter df
    parameter_df = pd.DataFrame(columns=['file', 'serial', 'date', 'time', 'intensity', 'pmp', 'imp', 'vmp', 'voc', 'isc'])
    
    # Iterate through files
    for file in files:
        file_actual = file
        if batch_data_dict['initial_basename_underscore']:
            file_actual = file_actual.replace('-', '_', 1)
        print(f"Analyzing {file_actual}")
        filepath = f"{dir}/{file_actual}"
        for sun in sun_list:
            data_dict = {}
            metadata = get_filename_metadata(file)
            data_dict['file'] = basename(file)
            data_dict['serial'] = metadata['serial_number']
            data_dict['date'] = metadata['date']
            data_dict['time'] = metadata['time']

            corrected_data, mfi_contents = S.iv_analysis(mfr_file=filepath, reference_constant=None, voltage_temperature_coefficient=None, rsh_v_cell=batch_data_dict['rsh_v_cell'], step=batch_data_dict['step'], sun=sun)

            data_dict['intensity'] = float(corrected_data['intensity_array'])
            data_dict['pmp'] = float(corrected_data['intensity_pmp'])
            data_dict['imp'] = float(corrected_data['intensity_imp'])
            data_dict['vmp'] = float(corrected_data['intensity_vmp'])
            data_dict['voc'] = float(corrected_data['intensity_voc'])
            data_dict['isc'] = float(corrected_data['intensity_isc'])

            parameter_df.loc[len(parameter_df)] = data_dict

    return parameter_df

def exclude_modules(mods_to_exclude, df):
    '''
    Removes specified modules from the DataFrame based on serial numbers.

    Parameters
    ----------
    mods_to_exclude : list of str
        Serial numbers of modules to exclude.
    df : pandas.DataFrame
        DataFrame containing module data, including a 'serial' column.

    Returns
    -------
    df : pandas.DataFrame
        Filtered DataFrame with specified modules removed.
    '''
    if mods_to_exclude:
        df = df[~df['serial'].isin(mods_to_exclude)].reset_index(drop=True)

    return df

def subset_by_intensity(df, sun, margin):
    '''
    Filters the DataFrame to include only rows within a margin of the target sun intensity.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing an 'intensity' column.
    sun : float
        Target sun intensity value.
    margin : float
        Allowed deviation from the target sun intensity.

    Returns
    -------
    pandas.DataFrame
        Subset of the original DataFrame within the specified intensity range.
    '''
    return df[np.abs(df['intensity'] - sun) < margin].copy()

def get_control_data_at_intensity(batch_data, sun):
    '''
    Computes average IV parameters for the control module at a specified sun intensity.

    Parameters
    ----------
    batch_data : pandas.DataFrame
        DataFrame containing module measurements and metadata.
    sun : float
        Target sun intensity value for filtering.

    Returns
    -------
    control_dict : dict
        Dictionary of average IV parameters for the control module at the specified intensity.
    '''
    control_dict = {}
    batch_data_sun = subset_by_intensity(batch_data, sun, 0.05)
    batch_data_sun_avg = batch_data_sun[(batch_data_sun['serial']==batch_data_dict['control'])].groupby('serial')[batch_data_dict['cols_to_calc']].mean()

    control_dict['pmp'] = batch_data_sun_avg['pmp'].iloc[0]
    control_dict['imp'] = batch_data_sun_avg['imp'].iloc[0]
    control_dict['vmp'] = batch_data_sun_avg['vmp'].iloc[0]
    control_dict['isc'] = batch_data_sun_avg['isc'].iloc[0]
    control_dict['voc'] = batch_data_sun_avg['voc'].iloc[0]
    
    return control_dict

def compute_summary_stat(table, col, stat='mean', exclude_sers=None):
    '''
    Computes a summary statistic for a specified column, with optional exclusion of serials.

    Parameters
    ----------
    table : pandas.DataFrame
        DataFrame containing the data.
    col : str
        Column name to compute the statistic on.
    stat : str, optional
        Statistic to compute ('mean' or 'median'). Default is 'mean'.
    exclude_sers : list of str, optional
        Serial numbers to exclude from the calculation.

    Returns
    -------
    float
        Computed statistic rounded to three decimal places, or 0 if stat is unrecognized.
    '''
    if exclude_sers != None:
        table = table[~table['serial'].isin(exclude_sers)]

    # Update this with new stats as necessary
    recognized_stats = ['mean', 'median']
        
    if stat.lower() == 'mean':
        return round(table[col].mean(), 3)
    elif stat.lower() == 'median':
        return round(table[col].median(), 3)
    else:
        print(f"Unrecognized stat... try one of f{recognized_stats}")
        return 0

def output_summary_stats(table, cols, exclude_sers):
    '''
    Generates a summary table of mean and median statistics for specified columns, with and without excluded serials.

    Parameters
    ----------
    table : pandas.DataFrame
        DataFrame containing the data.
    cols : list of str
        Column names to compute statistics for.
    exclude_sers : list of str
        Serial numbers to exclude from the "w/o underperforming" calculations.

    Returns
    -------
    summary_df : pandas.DataFrame
        DataFrame of summary statistics indexed by statistic type.
    '''
    summary_df = pd.DataFrame()
    idx_cols = ['mean', 'mean (w/o underperforming)', 'median', 'median (w/o underperforming)']
    for col in cols:
        stats = []
        stats.append(compute_summary_stat(table, col, 'mean'))
        stats.append(compute_summary_stat(table, col, 'mean', exclude_sers))
        stats.append(compute_summary_stat(table, col, 'median'))
        stats.append(compute_summary_stat(table, col, 'median', exclude_sers))
        summary_df[col] = stats

    summary_df.index = idx_cols
    return summary_df

def norm_to_nameplate(nameplate_dict, params, df):
    '''
    Normalizes parameter values to nameplate ratings.

    Parameters
    ----------
    nameplate_dict : dict
        Dictionary of nameplate values keyed by parameter name.
    params : list of str
        List of parameter names to normalize.
    df : pandas.DataFrame
        DataFrame containing the raw parameter values.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with added columns showing percent of nameplate for each parameter.
    '''
    for param in batch_data_dict['cols_to_calc']:
        df[f'{param}_pct_namepl'] = df[param].map(lambda x: x / nameplate_dict[f'{param}_nameplate'])

    return df

def norm_to_control(control_dict, params, df):
    '''
    Normalizes parameter values to control module performance.

    Parameters
    ----------
    control_dict : dict
        Dictionary of control module parameter values keyed by name.
    params : list of str
        List of parameter names to normalize.
    df : pandas.DataFrame
        DataFrame containing the raw parameter values.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with added columns showing percent of control value for each parameter.
    '''
    for param in batch_data_dict['cols_to_calc']:
        df[f'{param}_pct_norm'] = df[param].map(lambda x: x / control_dict[f'{param}'])

    return df

def compute_plr(intensity, nameplate, measured, years):
    '''
    Computes performance loss rate (PLR) based on measured and nameplate values over time.

    Parameters
    ----------
    intensity : float
        Measured light intensity.
    nameplate : float
        Nameplate parameter value at 1 sun.
    measured : float
        Actual measured parameter value.
    years : float
        Time in years over which degradation is measured.

    Returns
    -------
    float
        Computed PLR value, rounded to six decimal places.
    '''
    namepl_sun = intensity * nameplate
    pct_namepl = measured / namepl_sun
    plr = 1 - np.power(pct_namepl, 1/years)
    rounded_plr = round(plr, 6)
     
    return rounded_plr

def compute_row(row, params):
    '''
    Applies performance loss rate (PLR) computation across all relevant parameters in a row.

    Parameters
    ----------
    row : pandas.Series
        Row containing intensity, measured parameters, and required metadata.

    Returns
    -------
    row : pandas.Series
        Row updated with PLR values for each parameter.
    '''
    for param in params:
        row[f'{param}_plr'] = compute_plr(row['mapped_intensity'], batch_data_dict[f'{param}_nameplate'], row[param], years=batch_data_dict['years'])
        
    return row

def round_intensity(intensity_col, increment):
    '''
    Rounds intensity values to the nearest specified increment.

    Parameters
    ----------
    intensity_col : pandas.Series
        Series of intensity values to round.
    increment : float
        Step size to round to (e.g., 0.05 rounds to nearest 0.05).

    Returns
    -------
    pandas.Series
        Series of rounded intensity values.
    '''
    inc_scaled = increment * 100
    
    return intensity_col.map(lambda x: round((x * 100) / inc_scaled) * inc_scaled / 100)

def get_serial_file(serial, iv_mfr, iv_dir): 
    files = [file for file in iv_mfr if serial in file]
    return f"{iv_dir}/{files[0]}"
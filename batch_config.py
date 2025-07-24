# batch_config.py

batch_data_dict = {
    'identifier': 'OCCC',
    'iv_dir': 'occc',
    'initial_basename_underscore': False,
    'has_basename_comment': True,
    'control': None,
    'modules_to_exclude': ['408181737'],
    'underperforming_serials': ['408106229', '408203627'],
    'cols_to_calc': ['pmp', 'imp', 'vmp', 'isc', 'voc'],
    'pmp_nameplate': 175,
    'vmp_nameplate': 35.4,
    'imp_nameplate': 4.95,
    'voc_nameplate': 44.6,
    'isc_nameplate': 5.43,
    'years': 19,
    'suns_to_iter': [0.4, 0.6, 0.8, 1],
    'rsh_v_cell': 0.45, # for S.iv_analysis()
    'step': 1, # for S.iv_analysis()
}
import itertools
import numpy as np
import pandas as pd

def get_data_for_signal(data,indicator,only_params=False):
    if indicator=='rsi_ma_short':
        parameters = {
            'rsi_length': range(data['rsi_length']['min'],data['rsi_length']['max']+1,data['rsi_length']['step']),
            'ma_length': range(data['ma_length']['min'],data['ma_length']['max']+1,data['ma_length']['step']),
            'MA_type': data['MA_type'],
            'rsi_type': data['rsi_type'],
            'break_sell': data['break_sell'],
            'rsi_upper': data['rsi_upper']

        }

        if only_params: return parameters
    combinations = list(itertools.product(*parameters.values()))
    data_for_signal_list = [dict(zip(parameters.keys(), combination)) for combination in combinations]
    return data_for_signal_list


def clear_combinations(data_signals,df):
    comb_df=pd.DataFrame(data_signals)
    df=df[['rsi_length','ma_length','MA_type','rsi_type','break_sell','rsi_upper']]
    missing_combinations_df = comb_df.merge(
        df,
        on=['rsi_length', 'ma_length', 'MA_type', 'rsi_type','break_sell','rsi_upper'],
        how='left',
        indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return missing_combinations_df.to_dict(orient='records')
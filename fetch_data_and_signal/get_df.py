import pandas as pd



def get_df_from_path(coin,folder_path):
    df = pd.read_csv(f'{folder_path}/{coin}.csv', index_col='Open time', parse_dates=True)
    return df

def get_df(folder_path,coin,date_range):
    df = get_df_from_path(coin,folder_path)
    start_date, end_date = date_range.split('/')
    df_filtered = df[(df.index > start_date) & (df.index < end_date)]

    return df_filtered


def proof_date_range(folder_path,coin,date_range):
    df = get_df_from_path(coin,folder_path)
    if date_range.split('/')[0]=='2020-1-1': return True
    start_date, end_date = pd.Timestamp(date_range.split('/')[0]), pd.Timestamp(date_range.split('/')[1])
    df = df[(df.index > start_date)]
    df_dates = df.index.normalize()

    if df_dates[0] != start_date: return False
    return True

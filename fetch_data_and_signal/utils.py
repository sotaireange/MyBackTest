
def get_fieldnames(indicator):
    if indicator == 'rsi_ma_short':
        fieldnames = ['coin', 'rsi_length','ma_length','MA_type','rsi_type','break_sell','rsi_upper',
                      'pnl_perc','pnl_average_perc','sqn','moneydown','won','lost','winrate']

    return fieldnames

def timeframe_int_to_str(timeframe):
    timeframe=int(timeframe)
    timeframe_word='m'
    if timeframe >=60:
        timeframe_word='h'
        timeframe//=60
    return f'{timeframe}{timeframe_word}'


def get_patch_to_result(timeframe,indicator,date_range):
    start_date, end_date = date_range.split('/')[0],date_range.split('/')[1]
    timeframe=timeframe_int_to_str(timeframe)
    path = f"result/{indicator}/{timeframe}/{start_date}_{end_date}"
    return path



def get_row(coin,data_signal,res,indicator):
    if indicator=='rsi_ma_short':
        row = {
            'coin': coin,
            'rsi_length':data_signal['rsi_length'],
            'ma_length':data_signal['ma_length'],
            'MA_type':data_signal['MA_type'],
            'rsi_type':data_signal['rsi_type'],
            'break_sell':data_signal['break_sell'],
            'rsi_upper':data_signal['rsi_upper'],
            'pnl_perc': float(res.get('pnl_perc',0)),
            'pnl_average_perc': float(res.get('pnl_average_perc',0)),
            'sqn': float(res.get('sqn',0)),
            'moneydown': float(res.get('moneydown',0)),
            'won': float(res.get('won',0)),
            'lost': float(res.get('lost',0)),
            'winrate': float(res.get('winrate',0)),


        }
        return row

